from unittest.mock import MagicMock
import pytest

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


@pytest.fixture(name='metric_summary_provider')
def _metric_summary_provider(
    page_views_and_downloads_provider_mock: MagicMock
) -> MetricSummaryProvider:
    return MetricSummaryProvider(
        page_views_and_downloads_provider=page_views_and_downloads_provider_mock
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

    def test_should_return_views(
        self,
        metric_summary_provider: MetricSummaryProvider,
        page_views_and_downloads_provider_mock: MagicMock
    ):
        page_views_and_downloads_provider_mock.get_metric_total_for_article_id.return_value = (
            123
        )
        summary_dict = metric_summary_provider.get_summary_for_article_id(
            article_id='12345'
        )
        assert summary_dict['items'][0]['views'] == 123
        (
            page_views_and_downloads_provider_mock
            .get_metric_total_for_article_id
            .assert_called_with(
                article_id='12345',
                metric_name='page_views'
            )
        )
