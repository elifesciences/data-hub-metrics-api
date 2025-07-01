from unittest.mock import MagicMock, call
import pytest

from data_hub_metrics_api.crossref_citations_provider import CrossrefCitationsProvider
from data_hub_metrics_api.metric_summary_provider import (
    MetricSummaryProvider
)
from data_hub_metrics_api.page_views_and_downloads_provider import (
    PageViewsAndDownloadsProvider
)


@pytest.fixture(name='page_views_and_downloads_provider_mock')
def _page_views_and_downloads_provider_mock() -> MagicMock:
    return MagicMock(
        name='page_views_and_downloads_provider_mock',
        spec=PageViewsAndDownloadsProvider
    )


@pytest.fixture(name='crossref_citations_provider_mock')
def _crossref_citations_provider_mock() -> MagicMock:
    return MagicMock(
        name='crossref_citations_provider_mock',
        spec=CrossrefCitationsProvider
    )


@pytest.fixture(name='metric_summary_provider')
def _metric_summary_provider(
    page_views_and_downloads_provider_mock: MagicMock,
    crossref_citations_provider_mock: MagicMock
) -> MetricSummaryProvider:
    return MetricSummaryProvider(
        page_views_and_downloads_provider=page_views_and_downloads_provider_mock,
        crossref_citations_provider=crossref_citations_provider_mock
    )


class TestMetricSummaryProvider:
    def test_should_return_one_item(
        self,
        metric_summary_provider: MetricSummaryProvider
    ):
        summary_dict = metric_summary_provider.get_summary_for_article_id(
            article_id='12345'
        )
        assert summary_dict['total'] == 1
        assert len(summary_dict['items']) == 1

    def test_should_return_views_and_downloads(
        self,
        metric_summary_provider: MetricSummaryProvider,
        page_views_and_downloads_provider_mock: MagicMock
    ):
        page_views_and_downloads_provider_mock.get_metric_total_for_article_id.side_effect = (
            lambda article_id, metric_name: (
                123 if metric_name == 'page_views'
                else 12
            )
        )
        summary_dict = metric_summary_provider.get_summary_for_article_id(
            article_id='12345'
        )
        assert summary_dict['items'][0]['views'] == 123
        assert summary_dict['items'][0]['downloads'] == 12
        (
            page_views_and_downloads_provider_mock
            .get_metric_total_for_article_id
            .assert_has_calls([
                call(article_id='12345', metric_name='page_views'),
                call(article_id='12345', metric_name='downloads')
            ])
        )

    def test_should_return_citations_for_crossref(
        self,
        metric_summary_provider: MetricSummaryProvider,
        crossref_citations_provider_mock: MagicMock
    ):
        (
            crossref_citations_provider_mock
            .get_combined_citations_source_metric_for_article_id
            .return_value
        ) = {
            'service': 'Crossref',
            'uri': '',
            'citations': 5
        }
        summary_dict = metric_summary_provider.get_summary_for_article_id(
            article_id='12345'
        )
        assert summary_dict['items'][0]['crossref'] == 5
        (
            crossref_citations_provider_mock
            .get_combined_citations_source_metric_for_article_id
            .assert_called_once_with(article_id='12345')
        )
