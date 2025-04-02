import logging

from pathlib import Path
from time import monotonic
from typing import Sequence

import objsize

from data_hub_metrics_api.sql import get_sql_path
from data_hub_metrics_api.utils.bigquery import iter_dict_from_bq_query


LOGGER = logging.getLogger(__name__)


class CrossrefCitationsProvider:
    def __init__(
        self,
        gcp_project_name: str = 'elife-data-pipeline',
    ) -> None:
        self.gcp_project_name = gcp_project_name
        self.crossref_citations_query = (
            Path(get_sql_path('crossref_citations_query.sql')).read_text(encoding='utf-8')
        )

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
