from datetime import date
from typing import Iterator
from unittest.mock import ANY, MagicMock, call, patch
import pytest

from data_hub_metrics_api.page_views_and_downloads_provider import (
    PageViewsAndDownloadsProvider,
    get_query_with_replaced_number_of_days,
    get_query_with_replaced_number_of_months
)
import data_hub_metrics_api.page_views_and_downloads_provider as views_downloads_provider_module


@pytest.fixture(name='redis_client_mock', autouse=True)
def _redis_client_mock() -> MagicMock:
    return MagicMock(name='redis_client')


@pytest.fixture(name='redis_client_set_mock')
def _redis_client_set_mock(redis_client_mock: MagicMock) -> MagicMock:
    return redis_client_mock.set


@pytest.fixture(name='page_views_and_downloads_provider')
def _page_views_and_downloads_provider(
    redis_client_mock: MagicMock
) -> PageViewsAndDownloadsProvider:
    return PageViewsAndDownloadsProvider(redis_client_mock)


@pytest.fixture(name='get_bq_result_from_bq_query_mock', autouse=True)
def _get_bq_result_from_bq_query_mock() -> Iterator[MagicMock]:
    with patch.object(
        views_downloads_provider_module,
        'get_bq_result_from_bq_query'
    ) as mock:
        yield mock


class TestGetQueryWithReplacedNumberOfDays:
    def test_should_replace_number_of_days(self):
        assert get_query_with_replaced_number_of_days(
            'SELECT {number_of_days}',
            number_of_days=123
        ) == 'SELECT 123'


class TestGetQueryWithReplacedNumberOfMonths:
    def test_should_replace_number_of_months(self):
        assert get_query_with_replaced_number_of_months(
            'SELECT {number_of_months}',
            number_of_months=12
        ) == 'SELECT 12'


class TestPageViewsAndDownloadsProvider:
    def test_should_return_zero_for_total_page_views_if_no_page_views(
        self,
        page_views_and_downloads_provider: PageViewsAndDownloadsProvider,
        redis_client_mock: MagicMock
    ):
        redis_client_mock.get.return_value = None
        assert page_views_and_downloads_provider.get_page_view_total_for_article_id(
            article_id='12345'
        ) == 0

    def test_should_return_total_page_views_from_redis(
        self,
        page_views_and_downloads_provider: PageViewsAndDownloadsProvider,
        redis_client_mock: MagicMock
    ):
        redis_client_mock.get.return_value = '123'
        assert page_views_and_downloads_provider.get_page_view_total_for_article_id(
            article_id='12345'
        ) == 123
        redis_client_mock.get.assert_called_with('article:12345:page_views')

    def test_should_return_total_page_views_as_total_value(
        self,
        page_views_and_downloads_provider: PageViewsAndDownloadsProvider,
        redis_client_mock: MagicMock
    ):
        redis_client_mock.get.return_value = '123'
        result = page_views_and_downloads_provider.get_page_views_for_article_id_by_time_period(
            article_id='12345',
            by='day',
            per_page=10,
            page=1
        )
        assert result['totalValue'] == 123

    def test_should_put_page_view_and_download_totals_in_redis(
        self,
        get_bq_result_from_bq_query_mock: MagicMock,
        page_views_and_downloads_provider: PageViewsAndDownloadsProvider,
        redis_client_set_mock: MagicMock
    ):
        mock_bq_result = MagicMock()
        mock_bq_result.total_rows = 1
        mock_bq_result.__iter__.return_value = iter([{
            'article_id': '12345',
            'page_view_count': 5,
            'download_count': 2
        }])
        get_bq_result_from_bq_query_mock.return_value = mock_bq_result
        page_views_and_downloads_provider.refresh_page_view_and_download_totals()
        get_bq_result_from_bq_query_mock.assert_called_with(
            project_name=page_views_and_downloads_provider.gcp_project_name,
            query=page_views_and_downloads_provider.page_view_and_download_totals_query
        )
        redis_client_set_mock.assert_has_calls([
            call('article:12345:page_views', 5),
            call('article:12345:downloads', 2)
        ])

    def test_should_return_zero_if_there_are_no_page_views(
        self,
        page_views_and_downloads_provider: PageViewsAndDownloadsProvider
    ):
        assert page_views_and_downloads_provider.get_page_views_for_article_id_by_time_period(
            article_id='12345',
            by='day',
            per_page=10,
            page=1
        ) == {
            'totalPeriods': 0,
            'totalValue': ANY,
            'periods': []
        }

    def test_should_read_page_views_from_redis(
        self,
        page_views_and_downloads_provider: PageViewsAndDownloadsProvider,
        redis_client_mock: MagicMock
    ):
        redis_client_mock.hgetall.return_value = {
            '2023-10-01': '5',
            '2023-10-02': '10'
        }
        result = page_views_and_downloads_provider.get_page_views_for_article_id_by_time_period(
            article_id='12345',
            by='day',
            per_page=10,
            page=1
        )
        redis_client_mock.hgetall.assert_called_once_with('article:12345:page_views:by_date')
        assert result == {
            'totalPeriods': 2,
            'totalValue': ANY,
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
        page_views_and_downloads_provider: PageViewsAndDownloadsProvider,
        redis_client_mock: MagicMock
    ):
        redis_client_mock.hgetall.return_value = {
            '2023-10-01': '5',
            '2023-10-02': '10',
            '2023-10-03': '15'
        }

        result = page_views_and_downloads_provider.get_page_views_for_article_id_by_time_period(
            article_id='12345',
            by='day',
            per_page=2,
            page=1
        )

        assert result == {
            'totalPeriods': 3,
            'totalValue': ANY,
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
        page_views_and_downloads_provider: PageViewsAndDownloadsProvider,
        redis_client_mock: MagicMock
    ):
        redis_client_mock.hgetall.return_value = {
            '2023-10-01': '5',
            '2023-10-02': '10',
            '2023-10-03': '15'
        }

        result = page_views_and_downloads_provider.get_page_views_for_article_id_by_time_period(
            article_id='12345',
            by='day',
            per_page=2,
            page=2
        )

        assert result == {
            'totalPeriods': 3,
            'totalValue': ANY,
            'periods': [{
                'period': '2023-10-01',
                'value': 5
            }]
        }

    def test_should_return_empty_periods_if_selected_page_does_not_exist(
        self,
        page_views_and_downloads_provider: PageViewsAndDownloadsProvider,
        redis_client_mock: MagicMock
    ):
        redis_client_mock.hgetall.return_value = {
            '2023-10-01': '5',
            '2023-10-02': '10',
            '2023-10-03': '15'
        }

        result = page_views_and_downloads_provider.get_page_views_for_article_id_by_time_period(
            article_id='12345',
            by='day',
            per_page=2,
            page=3
        )

        assert result == {
            'totalPeriods': 3,
            'totalValue': ANY,
            'periods': []
        }

    def test_should_replace_number_of_days_in_query(
        self,
        get_bq_result_from_bq_query_mock: MagicMock,
        page_views_and_downloads_provider: PageViewsAndDownloadsProvider,
    ):
        mock_bq_result = MagicMock()
        mock_bq_result.total_rows = 0
        get_bq_result_from_bq_query_mock.return_value = mock_bq_result
        page_views_and_downloads_provider.refresh_data(number_of_days=123)
        get_bq_result_from_bq_query_mock.assert_called_with(
            project_name=page_views_and_downloads_provider.gcp_project_name,
            query=get_query_with_replaced_number_of_days(
                page_views_and_downloads_provider.page_views_query,
                number_of_days=123
            )
        )

    def test_should_put_data_in_redis(
        self,
        get_bq_result_from_bq_query_mock: MagicMock,
        page_views_and_downloads_provider: PageViewsAndDownloadsProvider,
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
        page_views_and_downloads_provider.refresh_data(number_of_days=3)
        redis_client_mock.hset.assert_called_once_with(
            'article:12345:page_views:by_date',
            '2023-10-01',
            5
        )

    def test_should_read_page_views_monthly_from_redis(
        self,
        page_views_and_downloads_provider: PageViewsAndDownloadsProvider,
        redis_client_mock: MagicMock
    ):
        redis_client_mock.hgetall.return_value = {
            '2023-10': '5',
            '2023-11': '10'
        }
        result = page_views_and_downloads_provider.get_page_views_for_article_id_by_time_period(
            article_id='12345',
            by='month',
            per_page=10,
            page=1
        )
        redis_client_mock.hgetall.assert_called_once_with('article:12345:page_views:by_month')
        assert result == {
            'totalPeriods': 2,
            'totalValue': ANY,
            'periods': [{
                'period': '2023-11',
                'value': 10
            }, {
                'period': '2023-10',
                'value': 5
            }]
        }

    def test_should_replace_number_of_months_in_query(
        self,
        get_bq_result_from_bq_query_mock: MagicMock,
        page_views_and_downloads_provider: PageViewsAndDownloadsProvider,
    ):
        mock_bq_result = MagicMock()
        mock_bq_result.total_rows = 0
        get_bq_result_from_bq_query_mock.return_value = mock_bq_result
        page_views_and_downloads_provider.refresh_page_views_monthly(number_of_months=12)
        get_bq_result_from_bq_query_mock.assert_called_with(
            project_name=page_views_and_downloads_provider.gcp_project_name,
            query=get_query_with_replaced_number_of_months(
                page_views_and_downloads_provider.page_views_monthly_query,
                number_of_months=12
            )
        )

    def test_should_put_data_in_redis_for_monthly_page_views(
        self,
        get_bq_result_from_bq_query_mock: MagicMock,
        page_views_and_downloads_provider: PageViewsAndDownloadsProvider,
        redis_client_mock: MagicMock
    ):
        mock_bq_result = MagicMock()
        mock_bq_result.total_rows = 1
        mock_bq_result.__iter__.return_value = iter([{
            'article_id': '12345',
            'year_month': '2023-10',
            'page_view_count': 5
        }])
        get_bq_result_from_bq_query_mock.return_value = mock_bq_result
        page_views_and_downloads_provider.refresh_page_views_monthly(number_of_months=3)
        redis_client_mock.hset.assert_called_once_with(
            'article:12345:page_views:by_month',
            '2023-10',
            5
        )

    def test_should_return_zero_for_total_downloads_if_no_downloads(
        self,
        page_views_and_downloads_provider: PageViewsAndDownloadsProvider,
        redis_client_mock: MagicMock
    ):
        redis_client_mock.get.return_value = None
        assert page_views_and_downloads_provider.get_download_total_for_article_id(
            article_id='12345'
        ) == 0

    def test_should_return_total_downloads_from_redis(
        self,
        page_views_and_downloads_provider: PageViewsAndDownloadsProvider,
        redis_client_mock: MagicMock
    ):
        redis_client_mock.get.return_value = '12'
        assert page_views_and_downloads_provider.get_download_total_for_article_id(
            article_id='12345'
        ) == 12
        redis_client_mock.get.assert_called_with('article:12345:downloads')

    def test_should_return_total_downloads_as_total_value(
        self,
        page_views_and_downloads_provider: PageViewsAndDownloadsProvider,
        redis_client_mock: MagicMock
    ):
        redis_client_mock.get.return_value = '12'
        result = page_views_and_downloads_provider.get_downloads_for_article_id_by_time_period(
            article_id='12345',
            by='day',
            per_page=10,
            page=1
        )
        assert result['totalValue'] == 12
