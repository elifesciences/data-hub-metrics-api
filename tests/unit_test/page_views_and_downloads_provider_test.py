from datetime import date
from unittest.mock import ANY, MagicMock, call
import pytest

from data_hub_metrics_api.page_views_and_downloads_provider import (
    MetricNameLiteral,
    PageViewsAndDownloadsProvider,
    get_query_with_replaced_number_of_days,
    get_query_with_replaced_number_of_months
)


# Note: this could be any of the valid metric names
METRIC_NAME_1: MetricNameLiteral = 'page_views'


@pytest.fixture(name='redis_client_scan_iter_mock')
def _redis_client_scan_iter_mock(redis_client_mock: MagicMock) -> MagicMock:
    return redis_client_mock.scan_iter


@pytest.fixture(name='page_views_and_downloads_provider')
def _page_views_and_downloads_provider(
    redis_client_mock: MagicMock
) -> PageViewsAndDownloadsProvider:
    return PageViewsAndDownloadsProvider(redis_client_mock)


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
        iter_dict_from_bq_query_with_progress_mock: MagicMock,
        page_views_and_downloads_provider: PageViewsAndDownloadsProvider,
        redis_client_pipeline_mock: MagicMock
    ):
        iter_dict_from_bq_query_with_progress_mock.return_value = iter([{
            'article_id': '12345',
            'page_view_count': 5,
            'download_count': 2
        }])
        page_views_and_downloads_provider.refresh_page_view_and_download_totals()
        iter_dict_from_bq_query_with_progress_mock.assert_called_with(
            project_name=page_views_and_downloads_provider.gcp_project_name,
            query=page_views_and_downloads_provider.page_view_and_download_totals_query,
            desc=ANY
        )

        redis_client_pipeline_mock.set.assert_has_calls([
            call('article:12345:page_views', 5),
            call('article:12345:downloads', 2)
        ])
        redis_client_pipeline_mock.execute.assert_called_once()

    def test_should_replace_number_of_days_in_query(
        self,
        iter_dict_from_bq_query_with_progress_mock: MagicMock,
        page_views_and_downloads_provider: PageViewsAndDownloadsProvider,
    ):
        page_views_and_downloads_provider.refresh_page_views_and_downloads_daily(number_of_days=123)
        iter_dict_from_bq_query_with_progress_mock.assert_called_with(
            project_name=page_views_and_downloads_provider.gcp_project_name,
            query=get_query_with_replaced_number_of_days(
                page_views_and_downloads_provider.page_views_and_downloads_daily_query,
                number_of_days=123
            ),
            desc=ANY
        )

    def test_should_put_data_in_redis_for_daily_page_views_and_downloads(
        self,
        iter_dict_from_bq_query_with_progress_mock: MagicMock,
        page_views_and_downloads_provider: PageViewsAndDownloadsProvider,
        redis_client_pipeline_mock: MagicMock
    ):
        iter_dict_from_bq_query_with_progress_mock.return_value = iter([{
            'article_id': '12345',
            'event_date': date.fromisoformat('2023-10-01'),
            'page_view_count': 5,
            'download_count': 2
        }])
        page_views_and_downloads_provider.refresh_page_views_and_downloads_daily(number_of_days=3)
        redis_client_pipeline_mock.hset.assert_has_calls([
            call('article:12345:page_views:by_date', '2023-10-01', 5),
            call('article:12345:downloads:by_date', '2023-10-01', 2)
        ])
        redis_client_pipeline_mock.execute.assert_called_once()

    def test_should_replace_number_of_months_in_query(
        self,
        iter_dict_from_bq_query_with_progress_mock: MagicMock,
        page_views_and_downloads_provider: PageViewsAndDownloadsProvider,
    ):
        page_views_and_downloads_provider.refresh_page_views_and_downloads_monthly(
            number_of_months=12
        )
        iter_dict_from_bq_query_with_progress_mock.assert_called_with(
            project_name=page_views_and_downloads_provider.gcp_project_name,
            query=get_query_with_replaced_number_of_months(
                page_views_and_downloads_provider.page_views_and_downloads_monthly_query,
                number_of_months=12
            ),
            desc=ANY
        )

    def test_should_put_data_in_redis_for_monthly_page_views_and_downloads(
        self,
        iter_dict_from_bq_query_with_progress_mock: MagicMock,
        page_views_and_downloads_provider: PageViewsAndDownloadsProvider,
        redis_client_pipeline_mock: MagicMock
    ):
        iter_dict_from_bq_query_with_progress_mock.return_value = iter([{
            'article_id': '12345',
            'year_month': '2023-10',
            'page_view_count': 5,
            'download_count': 2
        }])
        page_views_and_downloads_provider.refresh_page_views_and_downloads_monthly(
            number_of_months=3
        )
        redis_client_pipeline_mock.hset.assert_has_calls([
            call('article:12345:page_views:by_month', '2023-10', 5),
            call('article:12345:downloads:by_month', '2023-10', 2)
        ])
        redis_client_pipeline_mock.execute.assert_called_once()
