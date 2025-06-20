from typing import Iterator
from unittest.mock import MagicMock, patch

import pytest

from data_hub_metrics_api.utils import bigquery as bigquery_module


@pytest.fixture()
def mock_env() -> Iterator[dict]:
    env_dict: dict = {}
    with patch('os.environ', env_dict):
        yield env_dict


@pytest.fixture(name="bigquery_mock", autouse=True)
def _bigquery_mock() -> Iterator[MagicMock]:
    with patch.object(bigquery_module, "bigquery") as mock:
        yield mock
