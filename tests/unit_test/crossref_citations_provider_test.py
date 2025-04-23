from typing import Iterable, Iterator, Mapping
from unittest.mock import MagicMock, patch

import pytest

from data_hub_metrics_api import crossref_citations_provider as crossref_citations_provider_module
from data_hub_metrics_api.crossref_citations_provider import (
    BigQueryResultRow,
    CrossrefCitationsProvider,
    get_citation_counts_by_article_id_and_version_map
)


@pytest.fixture(name='iter_dict_from_bq_query_mock', autouse=True)
def _iter_dict_from_bq_query_mock() -> Iterator[MagicMock]:
    with patch.object(
        crossref_citations_provider_module,
        'iter_dict_from_bq_query'
    ) as mock:
        yield mock


@pytest.fixture(name='redis_client_mock')
def _redis_client_mock() -> MagicMock:
    return MagicMock(name='redis_client')


class TestGetCitationCountsByArticleIdAndVersionMap:
    def test_should_return_map_for_valid_data(self):
        bq_result: Iterable[BigQueryResultRow] = [
            {'article_id': '12345', 'version_number': '1', 'citation_count': 10},
        ]
        expected_result = {
            ('12345', '1'): 10,
        }
        result = get_citation_counts_by_article_id_and_version_map(bq_result)
        assert result == expected_result

    def test_should_return_empty_dict_for_empty_list(self):
        bq_result: Iterable[BigQueryResultRow] = []
        expected_result: Mapping[tuple[str, str], int] = {}
        result = get_citation_counts_by_article_id_and_version_map(bq_result)
        assert result == expected_result

    def test_should_create_map_entry_for_article_id_with_none_version_number(self):
        bq_result: Iterable[BigQueryResultRow] = [
            {'article_id': '12345', 'citation_count': 81, 'version_number': None}
        ]
        expected_result = {('12345', None): 81}
        result = get_citation_counts_by_article_id_and_version_map(bq_result)
        assert result == expected_result


class TestCrossrefCitationsProvider:
    def test_happy_path(self, redis_client_mock: MagicMock):
        redis_client_mock.hget.return_value = b'0'
        citation_provider = CrossrefCitationsProvider(redis_client=redis_client_mock)
        result = citation_provider.get_citations_source_metric_for_article_id_and_version('1234', 1)
        assert result == {
            "service": "Crossref",
            "uri": "https://doi.org/10.7554/eLife.1234.1",
            "citations": 0
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

    def test_should_get_data_from_redis(
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
            "service": "Crossref",
            "uri": "https://doi.org/10.7554/eLife.12345.1",
            "citations": 10
        }

    def test_should_return_zero_for_no_citations(
        self,
        redis_client_mock: MagicMock
    ):
        redis_client_mock.hget.return_value = None
        citation_provider = CrossrefCitationsProvider(redis_client=redis_client_mock)
        result = (
            citation_provider.get_citations_source_metric_for_article_id_and_version('12345', 1)
        )
        assert result['citations'] == 0
