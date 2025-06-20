# pylint: disable=duplicate-code
from datetime import date
import logging
from pathlib import Path
from typing import Literal, TypedDict

from tqdm import tqdm
from redis import Redis

from data_hub_metrics_api.api_router_typing import MetricTimePeriodResponseTypedDict

from data_hub_metrics_api.sql import get_sql_path
from data_hub_metrics_api.utils.bigquery import get_bq_result_from_bq_query

LOGGER = logging.getLogger(__name__)


class BigQueryResultRow(TypedDict):
    article_id: str
    event_date: date
    page_view_count: int


class PageViewsProvider:
    def __init__(
        self,
        redis_client: Redis,
        gcp_project_name: str = 'elife-data-pipeline'
    ):
        self.redis_client = redis_client
        self.gcp_project_name = gcp_project_name
        self.page_views_query = (
            Path(get_sql_path('page_views_query.sql')).read_text(encoding='utf-8')
        )

    def get_page_views_for_article_id_by_time_period(
        self,
        article_id: str,
        by: Literal['day', 'month'],
        per_page: int,
        page: int
    ) -> MetricTimePeriodResponseTypedDict:
        LOGGER.info(
            'page-views: article_id=%r, by=%r, per_page=%r, page=%r',
            article_id, by, per_page, page
        )
        page_views_by_date: dict = self.redis_client.hgetall(  # type: ignore[assignment]
            f'article:{article_id}:page_views:by_date'
        )
        sorted_page_views_by_date = sorted(
            page_views_by_date.items(),
            key=lambda item: item[0],  # Sort by date string
            reverse=True
        )
        page_start_index = (page - 1) * per_page
        page_end_index = page_start_index + per_page
        return {
            'totalPeriods': len(page_views_by_date),
            'totalValue': sum(int(value) for value in page_views_by_date.values()),
            'periods': [
                {
                    'period': date_str,
                    'value': int(value)
                }
                for date_str, value in sorted_page_views_by_date[
                    page_start_index:page_end_index
                ]
            ]
        }

    def refresh_data(
        self
    ) -> None:
        LOGGER.info('Refreshing page views data from BigQuery...')
        bq_result = get_bq_result_from_bq_query(
            project_name=self.gcp_project_name,
            query=self.page_views_query
        )
        total_rows = bq_result.total_rows
        LOGGER.info('Total rows from BigQuery: %d', total_rows)

        for row in tqdm(bq_result, total=total_rows, desc="Loading Redis"):
            self.redis_client.hset(
                f'article:{row['article_id']}:page_views:by_date',
                row['event_date'].isoformat(),
                row['page_view_count']  # type: ignore[arg-type]
            )
