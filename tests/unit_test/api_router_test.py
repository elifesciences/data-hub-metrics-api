from typing import Sequence
from unittest.mock import MagicMock
from fastapi import FastAPI
from fastapi.testclient import TestClient
import pytest

from data_hub_metrics_api.api_router import create_api_router
from data_hub_metrics_api.api_router_typing import MetricTimePeriodResponseTypedDict
from data_hub_metrics_api.citations_provider import CitationsProvider
from data_hub_metrics_api.page_views_and_downloads_provider import PageViewsAndDownloadsProvider


METRIC_TIME_PERIOD_RESPONSE_DICT_1: MetricTimePeriodResponseTypedDict = {
    'totalPeriods': 1,
    'totalValue': 1,
    'periods': []
}


@pytest.fixture(name='citations_provider_mock')
def _citations_provider_mock() -> MagicMock:
    return MagicMock(nam='citations_provider_mock', spec=CitationsProvider)


@pytest.fixture(name='page_views_and_downloads_provider_mock')
def _page_views_and_downloads_provider_mock() -> MagicMock:
    return MagicMock(
        name='page_views_and_downloads_provider_mock',
        spec=PageViewsAndDownloadsProvider
    )


def create_test_client(
    citations_provider_list: Sequence[CitationsProvider],
    page_views_and_downloads_provider: PageViewsAndDownloadsProvider
) -> TestClient:
    app = FastAPI()
    app.include_router(create_api_router(
        citations_provider_list=citations_provider_list,
        page_views_and_downloads_provider=page_views_and_downloads_provider
    ))
    client = TestClient(app)
    return client


@pytest.fixture(name='test_client')
def _test_client(
    citations_provider_mock: MagicMock,
    page_views_and_downloads_provider_mock: MagicMock
) -> TestClient:
    return create_test_client(
        citations_provider_list=[citations_provider_mock],
        page_views_and_downloads_provider=page_views_and_downloads_provider_mock
    )


class TestProvideCitations:
    def test_should_return_citation_counts_for_article_and_version(
        self,
        test_client: TestClient,
        citations_provider_mock: MagicMock
    ):
        (
            citations_provider_mock
            .get_citations_source_metric_for_article_id_and_version
            .return_value
        ) = {
            "service": "Crossref",
            "uri": "https://doi.org/10.7554/eLife.85111.2",
            "citations": 7
        }
        response = test_client.get('/metrics/article/85111/citations/version/2')
        response.raise_for_status()
        actual_response_json = response.json()
        assert actual_response_json == [
            citations_provider_mock
            .get_citations_source_metric_for_article_id_and_version
            .return_value
        ]

    def test_should_return_combined_citation_counts_for_article(
        self,
        test_client: TestClient,
        citations_provider_mock: MagicMock
    ):
        (
            citations_provider_mock
            .get_combined_citations_source_metric_for_article_id
            .return_value
        ) = {
            "service": "Crossref",
            "uri": "https://doi.org/10.7554/eLife.85111",
            "citations": 7
        }
        response = test_client.get('/metrics/article/85111/citations')
        response.raise_for_status()
        actual_response_json = response.json()
        assert actual_response_json == [
            citations_provider_mock
            .get_combined_citations_source_metric_for_article_id
            .return_value
        ]

    def test_should_return_elife_content_type(
        self,
        test_client: TestClient,
        citations_provider_mock: MagicMock
    ):
        (
            citations_provider_mock
            .get_citations_source_metric_for_article_id_and_version
            .return_value
        ) = {
            "service": "Crossref",
            "uri": "https://doi.org/10.7554/eLife.85111.2",
            "citations": 7
        }
        response = test_client.get('/metrics/article/85111/citations/version/2')
        response.raise_for_status()
        response_headers = response.headers
        expected_content_type = 'application/vnd.elife.metric-citations+json; version=1'
        assert response_headers['Content-Type'] == expected_content_type

    def test_should_return_downloads_by_article_id_and_time_period(
        self,
        test_client: TestClient,
        page_views_and_downloads_provider_mock: MagicMock
    ):
        (
            page_views_and_downloads_provider_mock
            .get_downloads_for_article_id_by_time_period
            .return_value
        ) = METRIC_TIME_PERIOD_RESPONSE_DICT_1
        response = test_client.get('/metrics/article/85111/downloads')
        response.raise_for_status()
        actual_response_json = response.json()
        assert actual_response_json == METRIC_TIME_PERIOD_RESPONSE_DICT_1

    def test_should_return_page_views_by_article_id_and_time_period(
        self,
        test_client: TestClient,
        page_views_and_downloads_provider_mock: MagicMock
    ):
        (
            page_views_and_downloads_provider_mock
            .get_page_views_for_article_id_by_time_period
            .return_value
        ) = METRIC_TIME_PERIOD_RESPONSE_DICT_1
        response = test_client.get('/metrics/article/85111/page-views')
        response.raise_for_status()
        actual_response_json = response.json()
        assert actual_response_json == METRIC_TIME_PERIOD_RESPONSE_DICT_1
