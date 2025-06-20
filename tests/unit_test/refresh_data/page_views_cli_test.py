from typing import Iterator
from unittest.mock import MagicMock, patch
import pytest
from data_hub_metrics_api.refresh_data.page_views_cli import main

import data_hub_metrics_api.refresh_data.page_views_cli as cli_module


@pytest.fixture(name="get_redis_client_mock", autouse=True)
def _get_redis_client_mock() -> Iterator[MagicMock]:
    with patch.object(cli_module, "get_redis_client") as mock:
        yield mock


@pytest.fixture(name="page_views_provider_class_mock", autouse=True)
def _page_views_provider_class_mock() -> Iterator[MagicMock]:
    with patch.object(cli_module, "PageViewsProvider") as mock:
        yield mock


@pytest.fixture(name="page_views_provider_mock")
def _page_views_provider_mock(
    page_views_provider_class_mock: MagicMock
) -> MagicMock:
    return page_views_provider_class_mock.return_value


class TestMain:
    def test_should_call_refresh_data_on_page_views_provider(
        self,
        page_views_provider_mock: MagicMock,
    ):
        main(['--number-of-days=123'])
        page_views_provider_mock.refresh_data.assert_called_with(
            number_of_days=123
        )
