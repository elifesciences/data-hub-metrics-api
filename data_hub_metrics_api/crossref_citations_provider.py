import logging

from pathlib import Path
from time import monotonic
from typing import Sequence

import objsize

from data_hub_metrics_api.api_router_typing import CitationsSourceMetricTypedDict
from data_hub_metrics_api.citations_provider import CitationsProvider
from data_hub_metrics_api.sql import get_sql_path
from data_hub_metrics_api.utils.bigquery import iter_dict_from_bq_query


LOGGER = logging.getLogger(__name__)


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
        self.crossref_citations_list = self._load_query_results_from_bq()

    def _load_query_results_from_bq(self) -> Sequence[dict]:
        LOGGER.info('Loading query results from BigQuery...')
        start_time = monotonic()
        result = list(iter_dict_from_bq_query(
            self.gcp_project_name,
            self.crossref_citations_query
        ))
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
        for citation in self.crossref_citations_list:
            if (
                citation['article_id'] == article_id
                and citation['version_number'] == str(version_number)
            ):
                return {
                    'service': self.name,
                    'uri': citation['url'],
                    'citations': citation['citation_count']
                }
        return {
            'service': self.name,
            'uri': '',
            'citations': 0
        }
