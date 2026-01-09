import logging
from typing import Annotated, Literal, Optional, Sequence
from fastapi import APIRouter, Query
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse, PlainTextResponse
from redis import Redis

from data_hub_metrics_api.api_router_typing import (
    CitationsResponseSequence,
    ContentTypeLiteral,
    MetricSummaryResponseTypedDict,
    MetricTimePeriodResponseTypedDict
)
from data_hub_metrics_api.citations_provider import CitationsProvider
from data_hub_metrics_api.page_views_and_downloads_provider import PageViewsAndDownloadsProvider
from data_hub_metrics_api.metric_summary_provider import MetricSummaryProvider
from data_hub_metrics_api.non_article_page_views_provider import NonArticlePageViewsProvider


LOGGER = logging.getLogger(__name__)


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


def create_api_router(
    redis_client: Redis,
    citations_provider_list: Sequence[CitationsProvider],
    page_views_and_downloads_provider: PageViewsAndDownloadsProvider,
    metric_summary_provider: MetricSummaryProvider,
    non_article_page_views_provider: NonArticlePageViewsProvider
) -> APIRouter:
    assert page_views_and_downloads_provider is not None
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
        by: Literal['day', 'month'] = 'day',
        per_page: PerPageQueryType = 20,
        page: PageQueryType = 1
    ) -> MetricTimePeriodResponseTypedDict:
        return page_views_and_downloads_provider.get_metric_for_article_id_by_time_period(
            article_id=article_id,
            metric_name='downloads',
            by=by,
            per_page=per_page,
            page=page
        )

    @router.get(
        '/metrics/article/{article_id}/page-views',
        response_class=MetricTimePeriodJsonResponse
    )
    def provide_page_views(
        article_id: str,
        by: Literal['day', 'month'] = 'day',
        per_page: PerPageQueryType = 20,
        page: PageQueryType = 1
    ) -> MetricTimePeriodResponseTypedDict:
        return page_views_and_downloads_provider.get_metric_for_article_id_by_time_period(
            article_id=article_id,
            metric_name='page_views',
            by=by,
            per_page=per_page,
            page=page
        )

    @router.get('/metrics/article/summary')
    def provide_summary_for_all_articles(
        per_page: PerPageQueryType = 20,
        page: PageQueryType = 1
    ) -> MetricSummaryResponseTypedDict:
        return metric_summary_provider.get_summary_for_all_articles(
            per_page=per_page,
            page=page
        )

    @router.get('/metrics/article/{article_id}/summary')
    def provide_summary(
        article_id: str
    ) -> MetricSummaryResponseTypedDict:
        LOGGER.info('summary: article_id=%r', article_id)
        return metric_summary_provider.get_summary_for_article_id(
            article_id=article_id
        )

    @router.get(
        '/metrics/{content_type}/{content_id}/page-views',
        response_class=MetricTimePeriodJsonResponse
    )
    def provide_page_views_by_content_type(
        content_type: ContentTypeLiteral,
        content_id: str,
        by: Literal['day', 'month'] = 'day'
    ) -> MetricTimePeriodResponseTypedDict:
        return non_article_page_views_provider.get_page_views_by_content_type(
            content_type=content_type,
            content_id=content_id,
            by=by
        )

    @router.get('/ping/metrics', response_class=PlainTextResponse)
    def ping_pong() -> Optional[str]:
        if redis_client.ping():
            return 'pong'
        return 'no pong available'

    return router
