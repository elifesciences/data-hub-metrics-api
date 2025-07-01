# pylint: disable=duplicate-code
from data_hub_metrics_api.api_router_typing import (
    MetricSummaryResponseTypedDict
)
from data_hub_metrics_api.page_views_and_downloads_provider import (
    PageViewsAndDownloadsProvider
)


class MetricSummaryProvider:
    def __init__(
        self,
        page_views_and_downloads_provider: PageViewsAndDownloadsProvider
    ):
        self.page_views_and_downloads_provider = page_views_and_downloads_provider

    def get_summary_for_article_id(
        self,
        article_id: str
    ) -> MetricSummaryResponseTypedDict:
        return {
            "total": 1,
            "items": [{
                "id": int(article_id),
                "views": self.page_views_and_downloads_provider.get_metric_total_for_article_id(
                    article_id=article_id,
                    metric_name='page_views'
                ),
                "downloads": 0,
                "crossref": 0,
                "pubmed": 0,
                "scopus": 0
            }]
        }
