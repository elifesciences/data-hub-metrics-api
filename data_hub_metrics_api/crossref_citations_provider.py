import logging

from typing import Iterable, Optional, TypedDict, cast, override

from redis import Redis

from data_hub_metrics_api.api_router_typing import CitationsSourceMetricTypedDict
from data_hub_metrics_api.citations_provider import CitationsProvider
from data_hub_metrics_api.sql import get_sql_query_from_file
from data_hub_metrics_api.utils import bigquery
from data_hub_metrics_api.utils.collections import iter_batch_iterable

LOGGER = logging.getLogger(__name__)

BATCH_SIZE = 1000


class BigQueryResultRow(TypedDict):
    article_id: str
    version_number: Optional[str]
    citation_count: int


class CrossrefCitationsProvider(CitationsProvider):
    def __init__(
        self,
        redis_client: Redis,
        name: str = 'Crossref',
        gcp_project_name: str = 'elife-data-pipeline',
    ) -> None:
        super().__init__(name=name)
        self.redis_client = redis_client
        self.gcp_project_name = gcp_project_name
        self.crossref_citations_query = get_sql_query_from_file('crossref_citations_query.sql')

    def get_citations_source_metric_for_article_id_and_version(
        self,
        article_id: str,
        version_number: int
    ) -> CitationsSourceMetricTypedDict:
        citation_count = int(self.redis_client.hget(
            f'article:{article_id}:crossref_citations',
            str(version_number)
        ) or b'0')  # type: ignore[arg-type]
        LOGGER.debug(
            'Citations for article_id=%s, version_number=%d: %d',
            article_id,
            version_number,
            citation_count
        )
        return {
            'service': self.name,
            'uri': f'https://doi.org/10.7554/eLife.{article_id}.{version_number}',
            'citations': citation_count
        }

    def get_combined_citations_source_metric_for_article_id(
        self,
        article_id: str
    ) -> CitationsSourceMetricTypedDict:
        citation_count = sum(
            int(count) for count in self.redis_client.hgetall(  # type: ignore[misc,union-attr]
                f'article:{article_id}:crossref_citations'
            ).values()
        )
        LOGGER.debug(
            'Combined citations for article_id=%s: %d',
            article_id,
            citation_count
        )
        return {
            'service': self.name,
            'uri': f'https://doi.org/10.7554/eLife.{article_id}',
            'citations': citation_count
        }

    @override
    def refresh_data(
        self,
        batch_size: int = BATCH_SIZE
    ) -> None:
        LOGGER.info('Refreshing citation data from BigQuery...')
        bq_result = cast(
            Iterable[BigQueryResultRow],
            bigquery.iter_dict_from_bq_query_with_progress(
                project_name=self.gcp_project_name,
                query=self.crossref_citations_query,
                desc='Loading Redis'
            )
        )
        with self.redis_client.pipeline() as pipe:
            LOGGER.debug('Redis pipeline %r', pipe)
            for batch in iter_batch_iterable(bq_result, batch_size=batch_size):
                LOGGER.debug('Processing batch...')
                for row in batch:
                    LOGGER.debug('Processing row in batch...')
                    pipe.hset(
                        f'article:{row["article_id"]}:crossref_citations',
                        row.get('version_number') or '',
                        row['citation_count']  # type: ignore[arg-type]
                    )
                pipe.execute()

        LOGGER.info('Done: Refreshing citation data from BigQuery')
