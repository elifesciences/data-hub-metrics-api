from datetime import date
import logging
import re
from typing import Literal, Optional, Sequence, TypedDict

from redis import Redis

from data_hub_metrics_api.api_router_typing import MetricTimePeriodResponseTypedDict

from data_hub_metrics_api.sql import get_sql_query_file
from data_hub_metrics_api.utils.bigquery import iter_dict_from_bq_query_with_progress


LOGGER = logging.getLogger(__name__)


MetricNameLiteral = Literal['page_views', 'downloads']
BATCH_SIZE = 1000


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


def get_article_id_from_page_views_total_key(key: str) -> str:
    match = re.match(r'article:(\d+):page_views', key)
    if not match:
        raise ValueError(f'Invalid key format: {key}')
    return match.group(1)


class PageViewsAndDownloadsProvider:
    def __init__(
        self,
        redis_client: Redis,
        gcp_project_name: str = 'elife-data-pipeline'
    ):
        self.redis_client = redis_client
        self.gcp_project_name = gcp_project_name
        self.page_view_and_download_totals_query = (
            get_sql_query_file('page_view_and_download_totals_query.sql')
        )

        self.page_views_and_downloads_daily_query = (
            get_sql_query_file('page_views_and_downloads_daily_query.sql')
        )
        self.page_views_and_downloads_monthly_query = (
           get_sql_query_file('page_views_and_downloads_monthly_query.sql')
        )

    def get_total_article_count(self) -> int:
        return sum(1 for _ in self.redis_client.scan_iter(match='article:*:page_views'))

    def get_article_ids(
        self,
        per_page: int = 20,
        page: int = 1
    ) -> Sequence[str]:
        LOGGER.info('get_article_ids: per_page=%r, page=%r', per_page, page)
        page_start_index = (page - 1) * per_page
        page_end_index = page_start_index + per_page
        return sorted([
            get_article_id_from_page_views_total_key(key.decode('utf-8'))
            for key in self.redis_client.scan_iter(match='article:*:page_views')
        ])[page_start_index:page_end_index]

    def get_metric_total_for_article_id(
        self,
        article_id: str,
        metric_name: MetricNameLiteral
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
        metric_name: MetricNameLiteral,
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

    def refresh_page_view_and_download_totals(self, batch_size: int = BATCH_SIZE) -> None:
        LOGGER.info('Refreshing page view and download totals data from BigQuery...')
        bq_result_iterable = iter_dict_from_bq_query_with_progress(
            project_name=self.gcp_project_name,
            query=self.page_view_and_download_totals_query,
            desc='Loading Redis'
        )
        with self.redis_client.pipeline() as pipe:
            for i, row in enumerate(bq_result_iterable, 1):
                pipe.set(
                    f'article:{row['article_id']}:page_views',
                    row['page_view_count']  # type: ignore[arg-type]
                )
                pipe.set(
                    f'article:{row['article_id']}:downloads',
                    row['download_count']  # type: ignore[arg-type]
                )
                if i % batch_size == 0:
                    pipe.execute()
            pipe.execute()

        LOGGER.info('Done: Refreshing page view and download totals data from BigQuery')

    def refresh_page_views_and_downloads_daily(
        self,
        number_of_days: int,
        batch_size: int = BATCH_SIZE
    ) -> None:
        LOGGER.info('Refreshing page views and downloads daily from BigQuery...')
        bq_result_iterable = iter_dict_from_bq_query_with_progress(
            project_name=self.gcp_project_name,
            query=get_query_with_replaced_number_of_days(
                self.page_views_and_downloads_daily_query,
                number_of_days=number_of_days
            ),
            desc='Loading Redis'
        )
        with self.redis_client.pipeline() as pipe:
            for i, row in enumerate(bq_result_iterable, 1):
                pipe.hset(
                    f'article:{row['article_id']}:page_views:by_date',
                    row['event_date'].isoformat(),
                    row['page_view_count']  # type: ignore[arg-type]
                )
                pipe.hset(
                    f'article:{row['article_id']}:downloads:by_date',
                    row['event_date'].isoformat(),
                    row['download_count']  # type: ignore[arg-type]
                )
                if i % batch_size == 0:
                    pipe.execute()
            pipe.execute()
        LOGGER.info('Done: Refreshing page views and dosnloads daily from BigQuery')

    def refresh_page_views_and_downloads_monthly(
        self,
        number_of_months: int,
        batch_size: int = BATCH_SIZE
    ) -> None:
        LOGGER.info('Refreshing monthly page views and downloads from BigQuery...')
        bq_result_iterable = iter_dict_from_bq_query_with_progress(
            project_name=self.gcp_project_name,
            query=get_query_with_replaced_number_of_months(
                self.page_views_and_downloads_monthly_query,
                number_of_months=number_of_months
            ),
            desc='Loading Redis'
        )
        with self.redis_client.pipeline() as pipe:
            for i, row in enumerate(bq_result_iterable, 1):
                pipe.hset(
                    f'article:{row['article_id']}:page_views:by_month',
                    row['year_month'],
                    row['page_view_count']  # type: ignore[arg-type]
                )
                pipe.hset(
                    f'article:{row['article_id']}:downloads:by_month',
                    row['year_month'],
                    row['download_count']  # type: ignore[arg-type]
                )
                if i % batch_size == 0:
                    pipe.execute()
            pipe.execute()
        LOGGER.info('Done: Refreshing monthly page views and downloads from BigQuery')
