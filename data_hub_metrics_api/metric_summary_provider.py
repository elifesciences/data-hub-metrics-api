# pylint: disable=duplicate-code
from data_hub_metrics_api.api_router_typing import MetricSummaryResponseTypedDict


class MetricSummaryProvider:
    def get_summary_for_article_id(
        self,
        article_id: str
    ) -> MetricSummaryResponseTypedDict:
        return {
            "total": 1,
            "items": [{
                "id": int(article_id),
                "views": 0,
                "downloads": 0,
                "crossref": 0,
                "pubmed": 0,
                "scopus": 0
            }]
        }
