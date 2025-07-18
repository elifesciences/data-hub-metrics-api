from typing import Iterator
from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient
import pytest

from data_hub_metrics_api import main as main_module
from data_hub_metrics_api.main import RedisEnvironmentVariables, create_app, get_redis_client


@pytest.fixture(name='redis_class_mock', autouse=True)
def _redis_class_mock() -> Iterator[MagicMock]:
    with patch.object(main_module, 'Redis') as redis_class_mock:
        yield redis_class_mock


class TestGetRedisClient:
    def test_should_use_localhost_by_default(self, redis_class_mock: MagicMock):
        get_redis_client()
        redis_class_mock.assert_called_with(
            host='localhost',
            port=6379
        )

    def test_should_read_host_and_port_from_env_variable(
        self,
        redis_class_mock: MagicMock,
        mock_env: dict
    ):
        mock_env[RedisEnvironmentVariables.HOST] = 'redis_host'
        mock_env[RedisEnvironmentVariables.PORT] = '12345'
        get_redis_client()
        redis_class_mock.assert_called_with(
            host='redis_host',
            port=12345
        )


def test_read_main():
    client = TestClient(create_app())
    response = client.get('/')
    assert response.status_code == 200
