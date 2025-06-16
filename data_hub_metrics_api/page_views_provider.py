# pylint: disable=duplicate-code
import logging
from typing import Literal

from data_hub_metrics_api.api_router_typing import MetricTimePeriodResponseTypedDict

LOGGER = logging.getLogger(__name__)


class PageViewsProvider:
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
        return {
            'totalPeriods': 0,
            'totalValue': 0,
            'periods': []
        }
