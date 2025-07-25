
# pylint: disable=duplicate-code
import logging
from typing import Literal, Optional

from data_hub_metrics_api.api_router_typing import (
    ContentTypeLiteral,
    MetricTimePeriodResponseTypedDict
)
from data_hub_metrics_api.sql import get_sql_query_from_file
from data_hub_metrics_api.utils import bigquery
from data_hub_metrics_api.utils.collections import iter_batch_iterable

LOGGER = logging.getLogger(__name__)

BATCH_SIZE = 1000


class NonArticlePageViewsProvider:
    def __init__(
        self,
        redis_client,
        gcp_project_name: str = 'elife-data-pipeline'
    ):
        self.redis_client = redis_client
        self.gcp_project_name = gcp_project_name
        self.non_article_page_view_totals_query = (
            get_sql_query_from_file('non_article_page_view_totals_query.sql')
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

    def refresh_non_article_page_view_totals(self, batch_size: int = BATCH_SIZE) -> None:
        LOGGER.info('Refreshing non-article page view totals data from BigQuery...')
        bq_result_iterable = bigquery.iter_dict_from_bq_query_with_progress(
            project_name=self.gcp_project_name,
            query=self.non_article_page_view_totals_query,
            desc='Loading Redis'
        )
        with self.redis_client.pipeline() as pipe:
            for batch in iter_batch_iterable(bq_result_iterable, batch_size=batch_size):
                for row in batch:
                    pipe.set(
                        f'non-article:{row['content_type']}:{row['content_id']}:page_views',
                        row['page_view_count']
                    )
                pipe.execute()
        LOGGER.info('Done: Refreshing non-article page view totals data from BigQuery')
