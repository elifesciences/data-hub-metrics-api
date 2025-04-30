from typing import Sequence
from unittest.mock import MagicMock
from fastapi import FastAPI
from fastapi.testclient import TestClient

from data_hub_metrics_api.api_router import create_api_router
from data_hub_metrics_api.citations_provider import CitationsProvider


def create_test_client(citations_provider_list: Sequence[CitationsProvider]) -> TestClient:
    app = FastAPI()
    app.include_router(create_api_router(citations_provider_list=citations_provider_list))
    client = TestClient(app)
    return client


class TestProvideCitations:
    def test_should_return_citation_counts_for_article_and_version(
        self
    ):
        citations_provider_mock = MagicMock(spec=CitationsProvider)
        (
            citations_provider_mock
            .get_citations_source_metric_for_article_id_and_version
            .return_value
        ) = {
            "service": "Crossref",
            "uri": "https://doi.org/10.7554/eLife.85111.2",
            "citations": 7
        }
        client = create_test_client(citations_provider_list=[citations_provider_mock])
        response = client.get('/metrics/article/85111/citations/version/2')
        response.raise_for_status()
        actual_response_json = response.json()
        assert actual_response_json == [
            citations_provider_mock
            .get_citations_source_metric_for_article_id_and_version
            .return_value
        ]

    def test_should_return_combined_citation_counts_for_article(
        self
    ):
        citations_provider_mock = MagicMock(spec=CitationsProvider)
        (
            citations_provider_mock
            .get_combined_citations_source_metric_for_article_id
            .return_value
        ) = {
            "service": "Crossref",
            "uri": "https://doi.org/10.7554/eLife.85111",
            "citations": 7
        }
        client = create_test_client(citations_provider_list=[citations_provider_mock])
        response = client.get('/metrics/article/85111/citations')
        response.raise_for_status()
        actual_response_json = response.json()
        assert actual_response_json == [
            citations_provider_mock
            .get_combined_citations_source_metric_for_article_id
            .return_value
        ]

    def test_should_return_elife_content_type(
        self
    ):
        client = create_test_client([])
        response = client.get('/metrics/article/85111/citations/version/2')
        response.raise_for_status()
        response_headers = response.headers
        expected_content_type = 'application/vnd.elife.metric-citations+json; version=2'
        assert response_headers['Content-Type'] == expected_content_type
