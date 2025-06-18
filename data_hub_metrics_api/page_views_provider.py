# pylint: disable=duplicate-code
import logging
from typing import Literal

from redis import Redis

from data_hub_metrics_api.api_router_typing import MetricTimePeriodResponseTypedDict

LOGGER = logging.getLogger(__name__)


class PageViewsProvider:
    def __init__(
        self,
        redis_client: Redis
    ):
        self.redis_client = redis_client

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
        return {
            'totalPeriods': len(page_views_by_date),
            'totalValue': sum(int(value) for value in page_views_by_date.values()),
            'periods': [
                {
                    'period': date_str,
                    'value': int(value)
                }
                for date_str, value in sorted_page_views_by_date[:per_page]
            ]
        }
