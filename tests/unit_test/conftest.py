import logging
from typing import Iterator
from unittest.mock import MagicMock, patch

import pytest

from data_hub_metrics_api import main as main_module
from data_hub_metrics_api.utils import bigquery as bigquery_module


@pytest.fixture(scope='session', autouse=True)
def setup_logging():
    logging.basicConfig(level='INFO')
    for name in ['tests', 'data_hub_metrics_api']:
        logging.getLogger(name).setLevel('DEBUG')


@pytest.fixture()
def mock_env() -> Iterator[dict]:
    env_dict: dict = {}
    with patch('os.environ', env_dict):
        yield env_dict


@pytest.fixture(name='bigquery_mock', autouse=True)
def _bigquery_mock() -> Iterator[MagicMock]:
    with patch.object(bigquery_module, 'bigquery') as mock:
        yield mock


@pytest.fixture(autouse=True)
def iter_dict_from_bq_query_with_progress_mock() -> Iterator[MagicMock]:
    with patch.object(
        bigquery_module,
        'iter_dict_from_bq_query_with_progress'
    ) as mock:
        yield mock


@pytest.fixture(name='redis_client_mock', autouse=True)
def _redis_client_mock() -> Iterator[MagicMock]:
    with patch.object(main_module, 'Redis') as mock:
        yield mock.return_value


@pytest.fixture(name='redis_client_pipeline_mock')
def _redis_client_pipeline_mock(redis_client_mock: MagicMock) -> MagicMock:
    return redis_client_mock.pipeline.return_value.__enter__.return_value


@pytest.fixture(name='redis_client_set_mock')
def _redis_client_set_mock(redis_client_mock: MagicMock) -> MagicMock:
    return redis_client_mock.set
