# pylint: disable=duplicate-code
from datetime import date
import logging
from pathlib import Path
from typing import Literal, Optional, TypedDict

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
    download_count: int


def get_query_with_replaced_number_of_days(
    query: str,
    number_of_days: int
) -> str:
    return query.replace(r'{number_of_days}', str(number_of_days))


def get_query_with_replaced_number_of_months(
    query: str,
    number_of_months: int
) -> str:
    return query.replace(r'{number_of_months}', str(number_of_months))


class PageViewsAndDownloadsProvider:
    def __init__(
        self,
        redis_client: Redis,
        gcp_project_name: str = 'elife-data-pipeline'
    ):
        self.redis_client = redis_client
        self.gcp_project_name = gcp_project_name
        self.page_view_and_download_totals_query = Path(
            get_sql_path('page_view_and_download_totals_query.sql')
        ).read_text(encoding='utf-8')

        self.page_views_and_downloads_daily_query = (
            Path(get_sql_path('page_views_and_downloads_daily_query.sql'))
            .read_text(encoding='utf-8')
        )
        self.page_views_monthly_query = (
            Path(get_sql_path('page_views_monthly_query.sql')).read_text(encoding='utf-8')
        )

    def get_metric_total_for_article_id(
        self,
        article_id: str,
        metric_name: Literal['page_views', 'downloads']
    ) -> int:
        LOGGER.debug('page-views: article_id=%r', article_id)
        redis_value: Optional[str] = self.redis_client.get(  # type: ignore[assignment]
            f'article:{article_id}:{metric_name}'
        )
        return int(redis_value or 0)

    def get_metric_for_article_id_by_time_period(
        self,
        article_id: str,
        *,
        metric_name: Literal['page_views', 'downloads'],
        by: Literal['day', 'month'],
        per_page: int,
        page: int
    ) -> MetricTimePeriodResponseTypedDict:
        LOGGER.info(
            'metric: article_id=%r, metric=%r, r, by=%r, per_page=%r, page=%r',
            metric_name, article_id, by, per_page, page
        )
        page_views_by_period: dict
        if by == 'month':
            page_views_by_period = self.redis_client.hgetall(  # type: ignore[assignment]
                f'article:{article_id}:{metric_name}:by_month'
            )
        else:
            page_views_by_period = self.redis_client.hgetall(  # type: ignore[assignment]
                f'article:{article_id}:{metric_name}:by_date'
            )
        sorted_page_views_by_period = sorted(
            page_views_by_period.items(),
            key=lambda item: item[0],  # Sort by date string or year month
            reverse=True
        )
        page_start_index = (page - 1) * per_page
        page_end_index = page_start_index + per_page
        total_value = self.get_metric_total_for_article_id(
            article_id,
            metric_name=metric_name
        )
        return {
            'totalPeriods': len(page_views_by_period),
            'totalValue': total_value,
            'periods': [
                {
                    'period': period_str,
                    'value': int(value)
                }
                for period_str, value in sorted_page_views_by_period[
                    page_start_index:page_end_index
                ]
            ]
        }

    def get_page_views_for_article_id_by_time_period(
        self,
        article_id: str,
        by: Literal['day', 'month'],
        per_page: int,
        page: int
    ) -> MetricTimePeriodResponseTypedDict:
        return self.get_metric_for_article_id_by_time_period(
            article_id=article_id,
            metric_name='page_views',
            by=by,
            per_page=per_page,
            page=page
        )

    def get_downloads_for_article_id_by_time_period(
        self,
        article_id: str,
        by: Literal['day', 'month'],
        per_page: int,
        page: int
    ) -> MetricTimePeriodResponseTypedDict:
        return self.get_metric_for_article_id_by_time_period(
            article_id=article_id,
            metric_name='downloads',
            by=by,
            per_page=per_page,
            page=page
        )

    def refresh_page_view_and_download_totals(self) -> None:
        LOGGER.info('Refreshing page view and download totals data from BigQuery...')
        bq_result = get_bq_result_from_bq_query(
            project_name=self.gcp_project_name,
            query=self.page_view_and_download_totals_query
        )
        total_rows = bq_result.total_rows
        LOGGER.info('Total rows from BigQuery: %d', total_rows)

        for row in tqdm(bq_result, total=total_rows, desc="Loading Redis"):
            self.redis_client.set(
                f'article:{row['article_id']}:page_views',
                row['page_view_count']  # type: ignore[arg-type]
            )
            self.redis_client.set(
                f'article:{row['article_id']}:downloads',
                row['download_count']  # type: ignore[arg-type]
            )
        LOGGER.info('Done: Refreshing page view and download totals data from BigQuery')

    def refresh_page_views_and_downloads_daily(
        self,
        number_of_days: int
    ) -> None:
        LOGGER.info('Refreshing page views and downloads daily from BigQuery...')
        bq_result = get_bq_result_from_bq_query(
            project_name=self.gcp_project_name,
            query=get_query_with_replaced_number_of_days(
                self.page_views_and_downloads_daily_query,
                number_of_days=number_of_days
            )
        )
        total_rows = bq_result.total_rows
        LOGGER.info('Total rows from BigQuery: %d', total_rows)

        for row in tqdm(bq_result, total=total_rows, desc="Loading Redis"):
            self.redis_client.hset(
                f'article:{row['article_id']}:page_views:by_date',
                row['event_date'].isoformat(),
                row['page_view_count']  # type: ignore[arg-type]
            )
            self.redis_client.hset(
                f'article:{row['article_id']}:downloads:by_date',
                row['event_date'].isoformat(),
                row['download_count']  # type: ignore[arg-type]
            )
        LOGGER.info('Done: Refreshing page views and dosnloads daily from BigQuery')

    def refresh_page_views_monthly(
        self,
        number_of_months: int
    ) -> None:
        LOGGER.info('Refreshing monthly page views data from BigQuery...')
        bq_result = get_bq_result_from_bq_query(
            project_name=self.gcp_project_name,
            query=get_query_with_replaced_number_of_months(
                self.page_views_monthly_query,
                number_of_months=number_of_months
            )
        )
        total_rows = bq_result.total_rows
        LOGGER.info('Total rows from BigQuery: %d', total_rows)

        for row in tqdm(bq_result, total=total_rows, desc="Loading Redis"):
            self.redis_client.hset(
                f'article:{row['article_id']}:page_views:by_month',
                row['year_month'],
                row['page_view_count']  # type: ignore[arg-type]
            )
        LOGGER.info('Done: Refreshing monthly page views data from BigQuery')
