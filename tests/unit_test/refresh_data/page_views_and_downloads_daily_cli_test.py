from typing import Iterator
from unittest.mock import MagicMock, patch
import pytest
from data_hub_metrics_api.refresh_data.page_views_and_downloads_daily_cli import main

import data_hub_metrics_api.refresh_data.page_views_and_downloads_daily_cli as cli_module


@pytest.fixture(name='page_views_and_downloads_provider_class_mock', autouse=True)
def _page_views_and_downloads_provider_class_mock() -> Iterator[MagicMock]:
    with patch.object(cli_module, 'PageViewsAndDownloadsProvider') as mock:
        yield mock


@pytest.fixture(name='page_views_and_downloads_provider_mock')
def _page_views_and_downloads_provider_mock(
    page_views_and_downloads_provider_class_mock: MagicMock
) -> MagicMock:
    return page_views_and_downloads_provider_class_mock.return_value


class TestMain:
    def test_should_call_refresh_data_on_page_views_and_downloads_provider(
        self,
        page_views_and_downloads_provider_mock: MagicMock,
    ):
        main(['--number-of-days=123'])
        (
            page_views_and_downloads_provider_mock
            .refresh_page_views_and_downloads_daily
            .assert_called_with(number_of_days=123)
        )
