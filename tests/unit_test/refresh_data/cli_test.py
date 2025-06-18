from typing import Iterable
from unittest.mock import MagicMock, patch
import pytest
from data_hub_metrics_api.refresh_data.cli import main

import data_hub_metrics_api.refresh_data.cli as cli_module


@pytest.fixture(name="get_redis_client_mock", autouse=True)
def _get_redis_client_mock() -> Iterable[MagicMock]:
    with patch.object(cli_module, "get_redis_client") as mock:
        yield mock


@pytest.fixture(name="get_citations_provider_list_mock", autouse=True)
def _get_citations_provider_list_mock() -> Iterable[MagicMock]:
    with patch.object(cli_module, "get_citations_provider_list") as mock:
        yield mock


class TestMain:
    def test_should_not_fail(self):
        main()

    def test_should_call_refresh_data(
        self,
        get_citations_provider_list_mock: MagicMock,
    ):
        provider = MagicMock(name="provider_1")
        get_citations_provider_list_mock.return_value = [provider]
        main()
        provider.refresh_data.assert_called_once()
