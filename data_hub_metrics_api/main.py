import logging
from typing import Sequence

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from redis import Redis

from data_hub_metrics_api.api_router import create_api_router
from data_hub_metrics_api.citations_provider import CitationsProvider, DummyCitationsProvider
from data_hub_metrics_api.crossref_citations_provider import CrossrefCitationsProvider


LOGGER = logging.getLogger(__name__)


def get_redis_client() -> Redis:
    redis_client = Redis()
    redis_client.ping()
    return redis_client


def get_citations_provider_list() -> Sequence[CitationsProvider]:
    return [
        CrossrefCitationsProvider(name="Crossref", redis_client=get_redis_client()),
        DummyCitationsProvider(name="PubMed Central"),
        DummyCitationsProvider(name="Scopus")
    ]


def create_app():
    app = FastAPI()

    citations_provider_list = get_citations_provider_list()

    app.include_router(create_api_router(citations_provider_list=citations_provider_list))

    app.mount('/', StaticFiles(directory='static', html=True), name='static')

    return app
