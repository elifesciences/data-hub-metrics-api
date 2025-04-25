from abc import ABC, abstractmethod

from data_hub_metrics_api.api_router_typing import CitationsSourceMetricTypedDict


class CitationsProvider(ABC):
    def __init__(self, name: str):
        super().__init__()
        self.name = name

    @abstractmethod
    def get_citations_source_metric_for_article_id_and_version(
        self,
        article_id: str,
        version_number: int
    ) -> CitationsSourceMetricTypedDict:
        pass

    def refresh_data(
        self
    ):
        pass


class DummyCitationsProvider(CitationsProvider):
    def get_citations_source_metric_for_article_id_and_version(
        self,
        article_id: str,
        version_number: int
    ) -> CitationsSourceMetricTypedDict:
        return {
            "service": self.name,
            "uri": "",
            "citations": 0
        }
