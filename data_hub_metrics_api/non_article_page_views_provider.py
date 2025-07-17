
import logging
from pathlib import Path
from typing import Literal, Optional

from tqdm import tqdm

from data_hub_metrics_api.api_router_typing import (
    ContentTypeLiteral,
    MetricTimePeriodResponseTypedDict
)
from data_hub_metrics_api.sql import get_sql_query_file
from data_hub_metrics_api.utils.bigquery import get_bq_result_from_bq_query

LOGGER = logging.getLogger(__name__)


class NonArticlePageViewsProvider:
    def __init__(
        self,
        redis_client,
        gcp_project_name: str = 'elife-data-pipeline'
    ):
        self.redis_client = redis_client
        self.gcp_project_name = gcp_project_name
        self.non_article_page_view_totals_query = (
            get_sql_query_file('non_article_page_view_totals_query.sql')
        )

    def get_page_views_by_content_type(
        self,
        content_type: ContentTypeLiteral,
        content_id: str,
        by: Literal['day', 'month'] = 'day'
    ) -> MetricTimePeriodResponseTypedDict:
        LOGGER.info(
            'page-views: content_type=%r, content_id=%r, by=%r',
            content_type,
            content_id,
            by
        )
        redis_value: Optional[str] = self.redis_client.get(  # type: ignore[assignment]
            f'non-article:{content_type}:{content_id}:page_views'
        )
        return {
            'totalPeriods': 0,
            'totalValue': int(redis_value or 0),
            'periods': []
        }

    def refresh_non_article_page_view_totals(self) -> None:
        LOGGER.info('Refreshing non-article page view totals data from BigQuery...')
        bq_result = get_bq_result_from_bq_query(
            project_name=self.gcp_project_name,
            query=self.non_article_page_view_totals_query
        )
        total_rows = bq_result.total_rows
        LOGGER.info('Total rows from BigQuery: %d', total_rows)

        for row in tqdm(bq_result, total=total_rows, desc="Loading Redis"):
            self.redis_client.set(
                f'non-article:{row["content_type"]}:{row["content_id"]}:page_views',
                row['page_view_count']
            )
        LOGGER.info('Done: Refreshing non-article page view totals data from BigQuery')
