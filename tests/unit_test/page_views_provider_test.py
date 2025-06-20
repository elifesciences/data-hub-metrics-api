from datetime import date
from typing import Iterator
from unittest.mock import MagicMock, patch
import pytest

from data_hub_metrics_api.page_views_provider import (
    PageViewsProvider,
    get_query_with_replaced_number_of_days
)
import data_hub_metrics_api.page_views_provider as page_views_provider_module


@pytest.fixture(name='redis_client_mock')
def _redis_client_mock() -> MagicMock:
    return MagicMock(name='redis_client')


@pytest.fixture(name='page_views_provider')
def _page_views_provider(redis_client_mock: MagicMock) -> PageViewsProvider:
    return PageViewsProvider(redis_client_mock)


@pytest.fixture(name='get_bq_result_from_bq_query_mock', autouse=True)
def _get_bq_result_from_bq_query_mock() -> Iterator[MagicMock]:
    with patch.object(
        page_views_provider_module,
        'get_bq_result_from_bq_query'
    ) as mock:
        yield mock


class TestGetQueryWithReplacedNumberOfDays:
    def test_should_replace_number_of_days(self):
        assert get_query_with_replaced_number_of_days(
            'SELECT {number_of_days}',
            number_of_days=123
        ) == 'SELECT 123'


class TestPageViewsProvider:
    def test_should_return_zero_if_there_are_no_page_views(
        self,
        page_views_provider: PageViewsProvider
    ):
        assert page_views_provider.get_page_views_for_article_id_by_time_period(
            article_id='12345',
            by='day',
            per_page=10,
            page=1
        ) == {
            'totalPeriods': 0,
            'totalValue': 0,
            'periods': []
        }

    def test_should_read_page_views_from_redis(
        self,
        page_views_provider: PageViewsProvider,
        redis_client_mock: MagicMock
    ):
        redis_client_mock.hgetall.return_value = {
            '2023-10-01': '5',
            '2023-10-02': '10'
        }
        result = page_views_provider.get_page_views_for_article_id_by_time_period(
            article_id='12345',
            by='day',
            per_page=10,
            page=1
        )
        redis_client_mock.hgetall.assert_called_once_with('article:12345:page_views:by_date')
        assert result == {
            'totalPeriods': 2,
            'totalValue': 15,
            'periods': [{
                'period': '2023-10-02',
                'value': 10
            }, {
                'period': '2023-10-01',
                'value': 5
            }]
        }

    def test_should_not_return_more_than_per_page_items(
        self,
        page_views_provider: PageViewsProvider,
        redis_client_mock: MagicMock
    ):
        redis_client_mock.hgetall.return_value = {
            '2023-10-01': '5',
            '2023-10-02': '10',
            '2023-10-03': '15'
        }

        result = page_views_provider.get_page_views_for_article_id_by_time_period(
            article_id='12345',
            by='day',
            per_page=2,
            page=1
        )

        assert result == {
            'totalPeriods': 3,
            'totalValue': 30,
            'periods': [{
                'period': '2023-10-03',
                'value': 15
            }, {
                'period': '2023-10-02',
                'value': 10
            }]
        }

    def test_should_not_return_from_selected_page_number(
        self,
        page_views_provider: PageViewsProvider,
        redis_client_mock: MagicMock
    ):
        redis_client_mock.hgetall.return_value = {
            '2023-10-01': '5',
            '2023-10-02': '10',
            '2023-10-03': '15'
        }

        result = page_views_provider.get_page_views_for_article_id_by_time_period(
            article_id='12345',
            by='day',
            per_page=2,
            page=2
        )

        assert result == {
            'totalPeriods': 3,
            'totalValue': 30,
            'periods': [{
                'period': '2023-10-01',
                'value': 5
            }]
        }

    def test_should_return_empty_periods_if_selected_page_does_not_exist(
        self,
        page_views_provider: PageViewsProvider,
        redis_client_mock: MagicMock
    ):
        redis_client_mock.hgetall.return_value = {
            '2023-10-01': '5',
            '2023-10-02': '10',
            '2023-10-03': '15'
        }

        result = page_views_provider.get_page_views_for_article_id_by_time_period(
            article_id='12345',
            by='day',
            per_page=2,
            page=3
        )

        assert result == {
            'totalPeriods': 3,
            'totalValue': 30,
            'periods': []
        }

    def test_should_replace_number_of_days_in_query(
        self,
        get_bq_result_from_bq_query_mock: MagicMock,
        page_views_provider: PageViewsProvider,
    ):
        mock_bq_result = MagicMock()
        mock_bq_result.total_rows = 0
        get_bq_result_from_bq_query_mock.return_value = mock_bq_result
        page_views_provider.refresh_data(number_of_days=123)
        get_bq_result_from_bq_query_mock.assert_called_with(
            project_name=page_views_provider.gcp_project_name,
            query=get_query_with_replaced_number_of_days(
                page_views_provider.page_views_query,
                number_of_days=123
            )
        )

    def test_should_put_data_in_redis(
        self,
        get_bq_result_from_bq_query_mock: MagicMock,
        page_views_provider: PageViewsProvider,
        redis_client_mock: MagicMock
    ):
        mock_bq_result = MagicMock()
        mock_bq_result.total_rows = 1
        mock_bq_result.__iter__.return_value = iter([{
            'article_id': '12345',
            'event_date': date.fromisoformat('2023-10-01'),
            'page_view_count': 5
        }])
        get_bq_result_from_bq_query_mock.return_value = mock_bq_result
        page_views_provider.refresh_data(number_of_days=3)
        redis_client_mock.hset.assert_called_once_with(
            'article:12345:page_views:by_date',
            '2023-10-01',
            5
        )
