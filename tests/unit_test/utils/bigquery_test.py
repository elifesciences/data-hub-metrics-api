from unittest.mock import MagicMock

import pytest

from google.cloud.bigquery.table import Row

from data_hub_metrics_api.utils.bigquery import iter_dict_from_bq_query


class RowIteratorMock:
    def __init__(self, items: list):
        self.items = items
        self.total_rows = len(items)

    def __iter__(self):
        return iter(self.items)


@pytest.fixture(name='bq_client_mock')
def _bq_client_mock(bigquery_mock: MagicMock) -> MagicMock:
    return bigquery_mock.Client


class TestIterDictFromBqQuery:
    def test_should_return_dict_for_row(self, bq_client_mock: MagicMock):
        mock_query_job = bq_client_mock.return_value.query.return_value
        mock_query_job.result.return_value = RowIteratorMock([
            Row(['value1', 'value2'], {'key1': 0, 'key2': 1})
        ])
        result = list(iter_dict_from_bq_query(
            project_name='project1',
            query='query1'
        ))
        assert result == [{
            'key1': 'value1',
            'key2': 'value2'
        }]
