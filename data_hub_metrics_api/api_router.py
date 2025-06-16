import logging
from typing import Literal, Sequence
from fastapi import APIRouter
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from data_hub_metrics_api.api_router_typing import (
    MetricSummaryResponseTypedDict,
    MetricTimePeriodResponseTypedDict
)
from data_hub_metrics_api.citations_provider import CitationsProvider


LOGGER = logging.getLogger(__name__)


ContentTypeLiteral = Literal[
    'blog-article',
    'labs-post',
    'collection',
    'digest',
    'event',
    'interview',
    'press-package'
]


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
    def provide_downloads(
        article_id: str,
        by: Literal['day', 'month'] = 'day'
    ) -> MetricTimePeriodResponseTypedDict:
        LOGGER.info('downloads: article_id=%r, by=%r', article_id, by)
        return {
            'totalPeriods': 0,
            'totalValue': 0,
            'periods': []
        }

    @router.get('/metrics/article/{article_id}/page-views')
    def provide_page_views(
        article_id: str,
        by: Literal['day', 'month'] = 'day'
    ) -> MetricTimePeriodResponseTypedDict:
        LOGGER.info('page-views: article_id=%r, by=%r', article_id, by)
        return {
            'totalPeriods': 0,
            'totalValue': 0,
            'periods': []
        }

    @router.get('/metrics/article/{article_id}/summary')
    def provide_summary(
        article_id: str
    ) -> MetricSummaryResponseTypedDict:
        LOGGER.info('summary: article_id=%r', article_id)
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

    @router.get('/metrics/{content_type}/{content_id}/page-views')
    def provide_page_views_by_content_type(
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

    return router
