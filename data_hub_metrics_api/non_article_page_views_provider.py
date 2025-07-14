
import logging
from typing import Literal

from data_hub_metrics_api.api_router_typing import (
    ContentTypeLiteral,
    MetricTimePeriodResponseTypedDict
)

LOGGER = logging.getLogger(__name__)


class NonArticlePageViewsProvider:
    def __init__(self):
        pass

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
        return {
            'totalPeriods': 0,
            'totalValue': 0,
            'periods': []
        }
