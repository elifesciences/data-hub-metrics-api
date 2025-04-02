from fastapi import FastAPI
from fastapi.testclient import TestClient

from data_hub_metrics_api.api_router import EXAMPLE_CITATIONS_RESPONSE, create_api_router
from data_hub_metrics_api.api_router_typing import CitationsResponseSequence


def create_test_client():
    app = FastAPI()
    app.include_router(create_api_router())
    client = TestClient(app)
    return client


class TestProvideCitations:
    def test_should_return_citation_counts(
        self
    ):
        expected_response_json: CitationsResponseSequence = EXAMPLE_CITATIONS_RESPONSE
        client = create_test_client()
        response = client.get('/elife-metrics/article/85111/citations/version/2')
        response.raise_for_status()
        actual_response_json = response.json()
        assert actual_response_json == expected_response_json
