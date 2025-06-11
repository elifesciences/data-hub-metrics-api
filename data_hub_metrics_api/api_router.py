from typing import Sequence
from fastapi import APIRouter
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from data_hub_metrics_api.api_router_typing import MetricTimePeriodResponseTypedDict
from data_hub_metrics_api.citations_provider import CitationsProvider


def create_api_router(citations_provider_list: Sequence[CitationsProvider]) -> APIRouter:
    router = APIRouter()

    @router.get('/metrics/article/{article_id}/citations/version/{version_number}')
    def provide_citations(article_id: str, version_number: int) -> JSONResponse:
        json_citation_response = jsonable_encoder([
            citations_provider.get_citations_source_metric_for_article_id_and_version(
                article_id=article_id,
                version_number=version_number
            )
            for citations_provider in citations_provider_list
        ])
        return JSONResponse(
            content=json_citation_response,
            headers={
                'Content-Type': 'application/vnd.elife.metric-citations+json; version=1'
            }
        )

    @router.get('/metrics/article/{article_id}/citations')
    def provide_combined_citations(article_id: str) -> JSONResponse:
        json_citation_response = jsonable_encoder([
            citations_provider.get_combined_citations_source_metric_for_article_id(
                article_id=article_id
            )
            for citations_provider in citations_provider_list
        ])
        return JSONResponse(
            content=json_citation_response,
            headers={
                'Content-Type': 'application/vnd.elife.metric-citations+json; version=1'
            }
        )

    @router.get('/metrics/article/{article_id}/downloads')
    def provide_downloads(_article_id: str) -> MetricTimePeriodResponseTypedDict:
        return {
            'totalPeriods': 0,
            'totalValue': 0,
            'periods': []
        }

    @router.get('/metrics/article/{article_id}/page-views')
    def provide_page_views(_article_id: str) -> MetricTimePeriodResponseTypedDict:
        return {
            'totalPeriods': 0,
            'totalValue': 0,
            'periods': []
        }

    return router
