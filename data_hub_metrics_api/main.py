import logging

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from data_hub_metrics_api.api_router import create_api_router
from data_hub_metrics_api.citations_provider import DummyCitationsProvider


LOGGER = logging.getLogger(__name__)


def create_app():
    app = FastAPI()

    citations_provider_list = [
        DummyCitationsProvider(name="Crossref"),
        DummyCitationsProvider(name="PubMed Central"),
        DummyCitationsProvider(name="Scopus")
    ]

    app.include_router(create_api_router(citations_provider_list=citations_provider_list))

    app.mount('/', StaticFiles(directory='static', html=True), name='static')

    return app
