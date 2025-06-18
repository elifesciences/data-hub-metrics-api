from unittest.mock import MagicMock
import pytest

from data_hub_metrics_api.page_views_provider import PageViewsProvider


@pytest.fixture(name='redis_client_mock')
def _redis_client_mock() -> MagicMock:
    return MagicMock(name='redis_client')


@pytest.fixture(name='page_views_provider')
def _page_views_provider(redis_client_mock) -> PageViewsProvider:
    return PageViewsProvider(redis_client_mock)


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
