from datetime import date
from typing import Iterator
from unittest.mock import ANY, MagicMock, call, patch
import pytest

from data_hub_metrics_api.page_views_and_downloads_provider import (
    MetricNameLiteral,
    PageViewsAndDownloadsProvider,
    get_query_with_replaced_number_of_days,
    get_query_with_replaced_number_of_months
)
import data_hub_metrics_api.page_views_and_downloads_provider as views_downloads_provider_module


# Note: this could be any of the valid metric names
METRIC_NAME_1: MetricNameLiteral = 'page_views'


@pytest.fixture(name='redis_client_mock', autouse=True)
def _redis_client_mock() -> MagicMock:
    return MagicMock(name='redis_client')


@pytest.fixture(name='redis_client_set_mock')
def _redis_client_set_mock(redis_client_mock: MagicMock) -> MagicMock:
    return redis_client_mock.set


@pytest.fixture(name='redis_client_pipeline_mock')
def _redis_client_pipeline_mock(redis_client_mock: MagicMock) -> MagicMock:
    return redis_client_mock.pipeline


@pytest.fixture(name='redis_client_hset_mock')
def _redis_client_hset_mock(redis_client_mock: MagicMock) -> MagicMock:
    return redis_client_mock.hset


@pytest.fixture(name='redis_client_scan_iter_mock')
def _redis_client_scan_iter_mock(redis_client_mock: MagicMock) -> MagicMock:
    return redis_client_mock.scan_iter


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


class TestGetArticleIds:
    def test_should_return_empty_article_ids_if_redis_is_empty(
        self,
        page_views_and_downloads_provider: PageViewsAndDownloadsProvider,
        redis_client_scan_iter_mock: MagicMock
    ):
        redis_client_scan_iter_mock.return_value = iter([])
        assert page_views_and_downloads_provider.get_article_ids(
            per_page=10,
            page=1
        ) == []

    def test_should_return_all_article_ids_if_less_than_a_page(
        self,
        page_views_and_downloads_provider: PageViewsAndDownloadsProvider,
        redis_client_scan_iter_mock: MagicMock
    ):
        redis_client_scan_iter_mock.return_value = iter([
            b'article:10001:page_views',
            b'article:10002:page_views',
            b'article:10003:page_views',
        ])
        assert page_views_and_downloads_provider.get_article_ids(
            per_page=10,
            page=1
        ) == ['10001', '10002', '10003']
        redis_client_scan_iter_mock.assert_called_once_with(
            match='article:*:page_views'
        )

    def test_should_not_return_article_ids_more_than_per_page_items(
        self,
        page_views_and_downloads_provider: PageViewsAndDownloadsProvider,
        redis_client_scan_iter_mock: MagicMock
    ):
        redis_client_scan_iter_mock.return_value = iter([
            b'article:10001:page_views',
            b'article:10002:page_views',
            b'article:10003:page_views'
        ])
        assert page_views_and_downloads_provider.get_article_ids(
            per_page=2,
            page=1
        ) == ['10001', '10002']
        redis_client_scan_iter_mock.assert_called_once_with(
            match='article:*:page_views'
        )

    def test_should_return_article_ids_from_selected_page_number(
        self,
        page_views_and_downloads_provider: PageViewsAndDownloadsProvider,
        redis_client_scan_iter_mock: MagicMock
    ):
        redis_client_scan_iter_mock.return_value = iter([
            b'article:10001:page_views',
            b'article:10002:page_views',
            b'article:10003:page_views'
        ])
        assert page_views_and_downloads_provider.get_article_ids(
            per_page=2,
            page=2
        ) == ['10003']
        redis_client_scan_iter_mock.assert_called_once_with(
            match='article:*:page_views'
        )

    def test_should_return_empty_article_ids_list_if_selected_page_does_not_exist(
        self,
        page_views_and_downloads_provider: PageViewsAndDownloadsProvider,
        redis_client_scan_iter_mock: MagicMock
    ):
        redis_client_scan_iter_mock.return_value = iter([
            b'article:10001:page_views',
            b'article:10002:page_views',
            b'article:10003:page_views'
        ])
        assert page_views_and_downloads_provider.get_article_ids(
            per_page=2,
            page=3
        ) == []


class TestGetMetricTotalForArticleId:
    def test_should_return_zero_for_total_metric_value_if_no_metric_value(
        self,
        page_views_and_downloads_provider: PageViewsAndDownloadsProvider,
        redis_client_mock: MagicMock
    ):
        redis_client_mock.get.return_value = None
        assert page_views_and_downloads_provider.get_metric_total_for_article_id(
            article_id='12345',
            metric_name=METRIC_NAME_1
        ) == 0

    def test_should_return_total_metric_value_from_redis(
        self,
        page_views_and_downloads_provider: PageViewsAndDownloadsProvider,
        redis_client_mock: MagicMock
    ):
        redis_client_mock.get.return_value = '123'
        assert page_views_and_downloads_provider.get_metric_total_for_article_id(
            article_id='12345',
            metric_name=METRIC_NAME_1
        ) == 123
        redis_client_mock.get.assert_called_with(f'article:12345:{METRIC_NAME_1}')


class TestGetMetricForArticleIdByTimePeriod:
    def test_should_return_total_metric_value_as_total_value(
        self,
        page_views_and_downloads_provider: PageViewsAndDownloadsProvider,
        redis_client_mock: MagicMock
    ):
        redis_client_mock.get.return_value = '123'
        result = page_views_and_downloads_provider.get_metric_for_article_id_by_time_period(
            article_id='12345',
            metric_name=METRIC_NAME_1,
            by='day',
            per_page=10,
            page=1
        )
        assert result['totalValue'] == 123

    def test_should_read_metric_periods_from_redis(
        self,
        page_views_and_downloads_provider: PageViewsAndDownloadsProvider,
        redis_client_mock: MagicMock
    ):
        redis_client_mock.hgetall.return_value = {
            '2023-10-01': '5',
            '2023-10-02': '10'
        }
        result = page_views_and_downloads_provider.get_metric_for_article_id_by_time_period(
            article_id='12345',
            metric_name=METRIC_NAME_1,
            by='day',
            per_page=10,
            page=1
        )
        redis_client_mock.hgetall.assert_called_once_with(f'article:12345:{METRIC_NAME_1}:by_date')
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

    def test_should_not_return_metric_periods_more_than_per_page_items(
        self,
        page_views_and_downloads_provider: PageViewsAndDownloadsProvider,
        redis_client_mock: MagicMock
    ):
        redis_client_mock.hgetall.return_value = {
            '2023-10-01': '5',
            '2023-10-02': '10',
            '2023-10-03': '15'
        }

        result = page_views_and_downloads_provider.get_metric_for_article_id_by_time_period(
            article_id='12345',
            metric_name=METRIC_NAME_1,
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

    def test_should_return_metric_periods_from_selected_page_number(
        self,
        page_views_and_downloads_provider: PageViewsAndDownloadsProvider,
        redis_client_mock: MagicMock
    ):
        redis_client_mock.hgetall.return_value = {
            '2023-10-01': '5',
            '2023-10-02': '10',
            '2023-10-03': '15'
        }

        result = page_views_and_downloads_provider.get_metric_for_article_id_by_time_period(
            article_id='12345',
            metric_name=METRIC_NAME_1,
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

    def test_should_return_empty_metric_periods_if_selected_page_does_not_exist(
        self,
        page_views_and_downloads_provider: PageViewsAndDownloadsProvider,
        redis_client_mock: MagicMock
    ):
        redis_client_mock.hgetall.return_value = {
            '2023-10-01': '5',
            '2023-10-02': '10',
            '2023-10-03': '15'
        }

        result = page_views_and_downloads_provider.get_metric_for_article_id_by_time_period(
            article_id='12345',
            metric_name=METRIC_NAME_1,
            by='day',
            per_page=2,
            page=3
        )

        assert result == {
            'totalPeriods': 3,
            'totalValue': ANY,
            'periods': []
        }


class TestPageViewsAndDownloadsProvider:
    def test_should_put_page_view_and_download_totals_in_redis(
        self,
        get_bq_result_from_bq_query_mock: MagicMock,
        page_views_and_downloads_provider: PageViewsAndDownloadsProvider,
        redis_client_pipeline_mock: MagicMock
    ):
        mock_bq_result = MagicMock()
        mock_bq_result.total_rows = 1
        mock_bq_result.__iter__.return_value = iter([{
            'article_id': '12345',
            'page_view_count': 5,
            'download_count': 2
        }])
        get_bq_result_from_bq_query_mock.return_value = mock_bq_result
        mock_pipeline = MagicMock()
        redis_client_pipeline_mock.return_value.__enter__.return_value = mock_pipeline

        page_views_and_downloads_provider.refresh_page_view_and_download_totals()
        get_bq_result_from_bq_query_mock.assert_called_with(
            project_name=page_views_and_downloads_provider.gcp_project_name,
            query=page_views_and_downloads_provider.page_view_and_download_totals_query
        )

        mock_pipeline.set.assert_has_calls([
            call('article:12345:page_views', 5),
            call('article:12345:downloads', 2)
        ])
        mock_pipeline.execute.assert_called_once()

    def test_should_replace_number_of_days_in_query(
        self,
        get_bq_result_from_bq_query_mock: MagicMock,
        page_views_and_downloads_provider: PageViewsAndDownloadsProvider,
    ):
        mock_bq_result = MagicMock()
        mock_bq_result.total_rows = 0
        get_bq_result_from_bq_query_mock.return_value = mock_bq_result
        page_views_and_downloads_provider.refresh_page_views_and_downloads_daily(number_of_days=123)
        get_bq_result_from_bq_query_mock.assert_called_with(
            project_name=page_views_and_downloads_provider.gcp_project_name,
            query=get_query_with_replaced_number_of_days(
                page_views_and_downloads_provider.page_views_and_downloads_daily_query,
                number_of_days=123
            )
        )

    def test_should_put_data_in_redis_for_daily_page_views_and_downloads(
        self,
        get_bq_result_from_bq_query_mock: MagicMock,
        page_views_and_downloads_provider: PageViewsAndDownloadsProvider,
        redis_client_pipeline_mock: MagicMock
    ):
        mock_bq_result = MagicMock()
        mock_bq_result.total_rows = 1
        mock_bq_result.__iter__.return_value = iter([{
            'article_id': '12345',
            'event_date': date.fromisoformat('2023-10-01'),
            'page_view_count': 5,
            'download_count': 2
        }])
        get_bq_result_from_bq_query_mock.return_value = mock_bq_result
        mock_pipeline = MagicMock()
        redis_client_pipeline_mock.return_value.__enter__.return_value = mock_pipeline
        page_views_and_downloads_provider.refresh_page_views_and_downloads_daily(number_of_days=3)
        mock_pipeline.hset.assert_has_calls([
            call('article:12345:page_views:by_date', '2023-10-01', 5),
            call('article:12345:downloads:by_date', '2023-10-01', 2)
        ])
        mock_pipeline.execute.assert_called_once()

    def test_should_replace_number_of_months_in_query(
        self,
        get_bq_result_from_bq_query_mock: MagicMock,
        page_views_and_downloads_provider: PageViewsAndDownloadsProvider,
    ):
        mock_bq_result = MagicMock()
        mock_bq_result.total_rows = 0
        get_bq_result_from_bq_query_mock.return_value = mock_bq_result
        page_views_and_downloads_provider.refresh_page_views_and_downloads_monthly(
            number_of_months=12
        )
        get_bq_result_from_bq_query_mock.assert_called_with(
            project_name=page_views_and_downloads_provider.gcp_project_name,
            query=get_query_with_replaced_number_of_months(
                page_views_and_downloads_provider.page_views_and_downloads_monthly_query,
                number_of_months=12
            )
        )

    def test_should_put_data_in_redis_for_monthly_page_views_and_downloads(
        self,
        get_bq_result_from_bq_query_mock: MagicMock,
        page_views_and_downloads_provider: PageViewsAndDownloadsProvider,
        redis_client_pipeline_mock: MagicMock
    ):
        mock_bq_result = MagicMock()
        mock_bq_result.total_rows = 1
        mock_bq_result.__iter__.return_value = iter([{
            'article_id': '12345',
            'year_month': '2023-10',
            'page_view_count': 5,
            'download_count': 2
        }])
        get_bq_result_from_bq_query_mock.return_value = mock_bq_result
        mock_pipeline = MagicMock()
        redis_client_pipeline_mock.return_value.__enter__.return_value = mock_pipeline
        page_views_and_downloads_provider.refresh_page_views_and_downloads_monthly(
            number_of_months=3
        )
        mock_pipeline.hset.assert_has_calls([
            call('article:12345:page_views:by_month', '2023-10', 5),
            call('article:12345:downloads:by_month', '2023-10', 2)
        ])
        mock_pipeline.execute.assert_called_once()
