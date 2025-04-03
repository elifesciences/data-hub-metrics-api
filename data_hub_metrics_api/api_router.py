from typing import Sequence
from fastapi import APIRouter

from data_hub_metrics_api.api_router_typing import CitationsResponseSequence
from data_hub_metrics_api.citations_provider import CitationsProvider


def create_api_router(citations_provider_list: Sequence[CitationsProvider]) -> APIRouter:
    router = APIRouter()

    @router.get('/metrics/article/{article_id}/citations/version/{version_number}')
    def provide_citations(article_id: str, version_number: int) -> CitationsResponseSequence:
        return [
            citations_provider.get_citations_source_metric_for_article_id_and_version(
                article_id=article_id,
                version_number=version_number
            )
            for citations_provider in citations_provider_list
        ]

    return router
