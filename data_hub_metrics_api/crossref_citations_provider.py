import logging

from typing import Iterable, Optional, TypedDict, cast, override

from redis import Redis

from data_hub_metrics_api.api_router_typing import CitationsSourceMetricTypedDict
from data_hub_metrics_api.citations_provider import CitationsProvider
from data_hub_metrics_api.sql import get_sql_query_file
from data_hub_metrics_api.utils.bigquery import iter_dict_from_bq_query

LOGGER = logging.getLogger(__name__)


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
        self.crossref_citations_query = get_sql_query_file('crossref_citations_query.sql')

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
        self
    ) -> None:
        LOGGER.info('Refreshing citation data from BigQuery...')
        bq_result = cast(
            Iterable[BigQueryResultRow],
            iter_dict_from_bq_query(
                self.gcp_project_name,
                self.crossref_citations_query
            )
        )
        for row in bq_result:
            self.redis_client.hset(
                f'article:{row['article_id']}:crossref_citations',
                row.get('version_number') or '',
                row['citation_count']  # type: ignore[arg-type]
            )
