import logging
from typing import Annotated, Literal, Sequence
from fastapi import APIRouter, Query
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from data_hub_metrics_api.api_router_typing import (
    CitationsResponseSequence,
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

PerPageQueryType = Annotated[
    int,
    # ge = greater than or equal to, le = less than or equal to
    Query(alias='per-page', ge=1, le=100)
]

PageQueryType = Annotated[
    int,
    # ge = greater than or equal to
    Query(alias='page', ge=1)
]


class CitationsJsonResponse(JSONResponse):
    media_type = 'application/vnd.elife.metric-citations+json; version=1'


class MetricTimePeriodJsonResponse(JSONResponse):
    media_type = 'application/vnd.elife.metric-time-period+json;version=1'


def create_api_router(citations_provider_list: Sequence[CitationsProvider]) -> APIRouter:
    router = APIRouter()

    @router.get(
        '/metrics/article/{article_id}/citations/version/{version_number}',
        response_class=CitationsJsonResponse
    )
    def provide_citations(article_id: str, version_number: int) -> CitationsResponseSequence:
        json_citation_response = jsonable_encoder([
            citations_provider.get_citations_source_metric_for_article_id_and_version(
                article_id=article_id,
                version_number=version_number
            )
            for citations_provider in citations_provider_list
        ])
        return json_citation_response

    @router.get(
        '/metrics/article/{article_id}/citations',
        response_class=CitationsJsonResponse
    )
    def provide_combined_citations(article_id: str) -> CitationsResponseSequence:
        json_citation_response = jsonable_encoder([
            citations_provider.get_combined_citations_source_metric_for_article_id(
                article_id=article_id
            )
            for citations_provider in citations_provider_list
        ])
        return json_citation_response

    @router.get(
        '/metrics/article/{article_id}/downloads',
        response_class=MetricTimePeriodJsonResponse
    )
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

    @router.get(
        '/metrics/article/{article_id}/page-views',
        response_class=MetricTimePeriodJsonResponse
    )
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

    @router.get('/metrics/article/summary')
    def provide_summary_for_all_articles(
        per_page: PerPageQueryType = 20,
        page: PageQueryType = 1
    ) -> MetricSummaryResponseTypedDict:
        LOGGER.info('summary: per_page=%r, page=%r', per_page, page)
        return {
            "total": 1,
            "items": [{
                "id": 12345,
                "views": 0,
                "downloads": 0,
                "crossref": 0,
                "pubmed": 0,
                "scopus": 0
            }]
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

    @router.get(
        '/metrics/{content_type}/{content_id}/page-views',
        response_class=MetricTimePeriodJsonResponse
    )
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
