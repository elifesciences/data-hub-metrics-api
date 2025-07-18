from typing import Iterator
from unittest.mock import MagicMock, patch
import pytest
from data_hub_metrics_api.refresh_data.citations_cli import main

import data_hub_metrics_api.refresh_data.citations_cli as cli_module


@pytest.fixture(name='get_citations_provider_list_mock', autouse=True)
def _get_citations_provider_list_mock() -> Iterator[MagicMock]:
    with patch.object(cli_module, 'get_citations_provider_list') as mock:
        yield mock


@pytest.mark.parametrize('get_redis_client_mock', [cli_module], indirect=True)
class TestMain:
    def test_should_call_refresh_data_on_citations_provider(
        self,
        get_redis_client_mock,  # pylint: disable=unused-argument
        get_citations_provider_list_mock: MagicMock,
    ):
        provider = MagicMock(name='provider_1')
        get_citations_provider_list_mock.return_value = [provider]
        main()
        provider.refresh_data.assert_called_once()
