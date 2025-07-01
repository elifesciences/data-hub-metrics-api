import logging
import os
from typing import Sequence

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from redis import Redis

from data_hub_metrics_api.api_router import create_api_router
from data_hub_metrics_api.citations_provider import CitationsProvider, DummyCitationsProvider
from data_hub_metrics_api.crossref_citations_provider import CrossrefCitationsProvider
from data_hub_metrics_api.page_views_and_downloads_provider import PageViewsAndDownloadsProvider
from data_hub_metrics_api.metric_summary_provider import MetricSummaryProvider


LOGGER = logging.getLogger(__name__)


class RedisEnvironmentVariables:
    HOST = 'REDIS_HOST'
    PORT = 'REDIS_PORT'


DEFAULT_REDIS_HOST = 'localhost'
DEFAULT_REDIS_PORT = 6379


def get_redis_client() -> Redis:
    host = os.getenv(RedisEnvironmentVariables.HOST) or DEFAULT_REDIS_HOST
    port = int(os.getenv(RedisEnvironmentVariables.PORT) or DEFAULT_REDIS_PORT)
    LOGGER.info('Connecting Redis to %s:%s', host, port)
    redis_client = Redis(host=host, port=port)
    redis_client.ping()
    return redis_client


def get_citations_provider_list(
    crossref_citations_provider: CrossrefCitationsProvider
) -> Sequence[CitationsProvider]:
    return [
        crossref_citations_provider,
        DummyCitationsProvider(name="PubMed Central"),
        DummyCitationsProvider(name="Scopus")
    ]


def create_app():
    app = FastAPI()

    redis_client = get_redis_client()

    page_views_and_downloads_provider = PageViewsAndDownloadsProvider(redis_client)
    crossref_citations_provider = CrossrefCitationsProvider(
        name="Crossref",
        redis_client=redis_client
    )
    citations_provider_list = get_citations_provider_list(crossref_citations_provider)

    app.include_router(create_api_router(
        citations_provider_list=citations_provider_list,
        page_views_and_downloads_provider=page_views_and_downloads_provider,
        metric_summary_provider=MetricSummaryProvider(
            page_views_and_downloads_provider=page_views_and_downloads_provider,
            crossref_citations_provider=crossref_citations_provider
        )
    ))

    app.mount('/', StaticFiles(directory='static', html=True), name='static')

    return app
