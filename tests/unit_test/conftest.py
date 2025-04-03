from typing import Iterable
from unittest.mock import MagicMock, patch

import pytest

from data_hub_metrics_api.utils import bigquery as bigquery_module


@pytest.fixture(name="bigquery_mock", autouse=True)
def _bigquery_mock() -> Iterable[MagicMock]:
    with patch.object(bigquery_module, "bigquery") as mock:
        yield mock
