import logging

from pathlib import Path
from time import monotonic
from typing import Iterable, Mapping

import objsize

from data_hub_metrics_api.api_router_typing import CitationsSourceMetricTypedDict
from data_hub_metrics_api.citations_provider import CitationsProvider
from data_hub_metrics_api.sql import get_sql_path
from data_hub_metrics_api.utils.bigquery import iter_dict_from_bq_query

LOGGER = logging.getLogger(__name__)


def get_citation_counts_by_article_id_and_version_map(
    bq_result: Iterable[dict]
) -> Mapping[tuple[str, str], int]:
    return {
        (row['article_id'], row['version_number']): row['citation_count']
        for row in bq_result
    }


class CrossrefCitationsProvider(CitationsProvider):
    def __init__(
        self,
        name: str = 'Crossref',
        gcp_project_name: str = 'elife-data-pipeline',
    ) -> None:
        super().__init__(name=name)
        self.gcp_project_name = gcp_project_name
        self.crossref_citations_query = (
            Path(get_sql_path('crossref_citations_query.sql')).read_text(encoding='utf-8')
        )
        self.citation_counts_by_article_id_and_version_map = self._load_query_results_from_bq()

    def _load_query_results_from_bq(self) -> Mapping[tuple[str, str], int]:
        LOGGER.info('Loading query results from BigQuery...')
        start_time = monotonic()
        bq_result = iter_dict_from_bq_query(
            self.gcp_project_name,
            self.crossref_citations_query
        )
        result = get_citation_counts_by_article_id_and_version_map(bq_result)
        end_time = monotonic()
        LOGGER.info(
            'Loaded query results from BigQuery, rows=%d, approx_size=%.3fMB, time=%.3f seconds',
            len(result),
            objsize.get_deep_size(result) / 1024 / 1024,
            (end_time - start_time)
        )
        return result

    def get_citations_source_metric_for_article_id_and_version(
        self,
        article_id: str,
        version_number: int
    ) -> CitationsSourceMetricTypedDict:
        citation_count = self.citation_counts_by_article_id_and_version_map.get(
            (article_id, str(version_number)),
            0
        )
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

    def refresh_data(
        self
    ) -> None:
        LOGGER.info('Refreshing citation data from BigQuery...')
