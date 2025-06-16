from abc import ABC, abstractmethod
from typing import Literal

from data_hub_metrics_api.api_router_typing import MetricTimePeriodResponseTypedDict


class PageViewsProvider(ABC):
    @abstractmethod
    def get_page_views_for_article_id_by_time_period(
        self,
        article_id: str,
        by: Literal['day', 'month'],
        per_page: int,
        page: int
    ) -> MetricTimePeriodResponseTypedDict:
        pass


class DummyPageViewsProvider(PageViewsProvider):
    def get_page_views_for_article_id_by_time_period(
        self,
        article_id: str,
        by: Literal['day', 'month'],
        per_page: int,
        page: int
    ) -> MetricTimePeriodResponseTypedDict:
        return {
            'totalPeriods': 0,
            'totalValue': 0,
            'periods': []
        }
