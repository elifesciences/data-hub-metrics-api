from typing import Iterable, Iterator
from unittest.mock import MagicMock, patch

import pytest

from data_hub_metrics_api import crossref_citations_provider as crossref_citations_provider_module
from data_hub_metrics_api.crossref_citations_provider import (
    BigQueryResultRow,
    CrossrefCitationsProvider
)


@pytest.fixture(name='redis_client_mock', autouse=True)
def _redis_client_mock() -> MagicMock:
    return MagicMock(name='redis_client')


@pytest.fixture(name='iter_dict_from_bq_query_mock', autouse=True)
def _iter_dict_from_bq_query_mock() -> Iterator[MagicMock]:
    with patch.object(
        crossref_citations_provider_module,
        'iter_dict_from_bq_query'
    ) as mock:
        yield mock


class TestCrossrefCitationsProvider:
    def test_happy_path(self, redis_client_mock: MagicMock):
        redis_client_mock.hget.return_value = b'0'
        citation_provider = CrossrefCitationsProvider(redis_client=redis_client_mock)
        result = citation_provider.get_citations_source_metric_for_article_id_and_version('1234', 1)
        assert result == {
            'service': 'Crossref',
            'uri': 'https://doi.org/10.7554/eLife.1234.1',
            'citations': 0
        }

    def test_should_put_data_in_redis(
        self,
        iter_dict_from_bq_query_mock: MagicMock
    ):
        bq_result: Iterable[BigQueryResultRow] = [
            {'article_id': '12345', 'version_number': '1', 'citation_count': 10},
        ]
        iter_dict_from_bq_query_mock.return_value = bq_result
        redis_client = MagicMock(name='redis_client')
        citation_provider = CrossrefCitationsProvider(redis_client=redis_client)
        citation_provider.refresh_data()
        redis_client.hset.assert_called_once_with(
            'article:12345:crossref_citations',
            '1',
            10
        )

    def test_should_get_data_from_redis_by_version(
        self,
        redis_client_mock: MagicMock
    ):
        redis_client_mock.hget.return_value = b'10'
        citation_provider = CrossrefCitationsProvider(redis_client=redis_client_mock)
        result = (
            citation_provider.get_citations_source_metric_for_article_id_and_version('12345', 1)
        )
        redis_client_mock.hget.assert_called_once_with(
            'article:12345:crossref_citations',
            '1'
        )
        assert result == {
            'service': 'Crossref',
            'uri': 'https://doi.org/10.7554/eLife.12345.1',
            'citations': 10
        }

    def test_should_return_zero_for_no_citations_by_version(
        self,
        redis_client_mock: MagicMock
    ):
        redis_client_mock.hget.return_value = None
        citation_provider = CrossrefCitationsProvider(redis_client=redis_client_mock)
        result = (
            citation_provider.get_citations_source_metric_for_article_id_and_version('12345', 1)
        )
        assert result['citations'] == 0

    def test_should_get_data_from_redis_by_article_id(
        self,
        redis_client_mock: MagicMock
    ):
        redis_client_mock.hgetall.return_value = {b'1': b'12', b'2': b'8', b'': b'43', b'3': b'3'}
        citation_provider = CrossrefCitationsProvider(redis_client=redis_client_mock)
        result = (
            citation_provider.get_combined_citations_source_metric_for_article_id('12345')
        )
        redis_client_mock.hgetall.assert_called_once_with('article:12345:crossref_citations')
        assert result == {
            'service': 'Crossref',
            'uri': 'https://doi.org/10.7554/eLife.12345',
            'citations': 12 + 8 + 43 + 3
        }

    def test_should_return_zero_for_no_citations_by_article_id(
        self,
        redis_client_mock: MagicMock
    ):
        redis_client_mock.hgetall.return_value = {}
        citation_provider = CrossrefCitationsProvider(redis_client=redis_client_mock)
        result = (
            citation_provider.get_combined_citations_source_metric_for_article_id('12345')
        )
        assert result['citations'] == 0
