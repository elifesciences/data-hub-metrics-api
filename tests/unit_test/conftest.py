from typing import Iterable
from unittest.mock import MagicMock, patch

import pytest

from data_hub_metrics_api.utils import bigquery as bigquery_module


@pytest.fixture()
def mock_env() -> Iterable[dict]:
    env_dict: dict = {}
    with patch('os.environ', env_dict):
        yield env_dict


@pytest.fixture(name="bigquery_mock", autouse=True)
def _bigquery_mock() -> Iterable[MagicMock]:
    with patch.object(bigquery_module, "bigquery") as mock:
        yield mock
