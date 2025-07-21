from typing import Iterator
from unittest.mock import ANY, MagicMock, patch

import pytest

import data_hub_metrics_api.non_article_page_views_provider as provider_module
from data_hub_metrics_api.api_router_typing import ContentTypeLiteral
from data_hub_metrics_api.non_article_page_views_provider import (
    NonArticlePageViewsProvider
)

CONTENT_TYPE_1: ContentTypeLiteral = 'blog-article'
CONTENT_ID_1 = 'content_id_1'


@pytest.fixture(name='redis_client_mock', autouse=True)
def _redis_client_mock() -> MagicMock:
    return MagicMock(name='redis_client')


@pytest.fixture(name='redis_client_set_mock')
def _redis_client_set_mock(redis_client_mock: MagicMock) -> MagicMock:
    return redis_client_mock.set


@pytest.fixture(name='redis_client_get_mock')
def _redis_client_get_mock(redis_client_mock: MagicMock) -> MagicMock:
    return redis_client_mock.get


@pytest.fixture(name='non_article_page_views_provider')
def _non_article_page_views_provider(
    redis_client_mock: MagicMock
) -> NonArticlePageViewsProvider:
    return NonArticlePageViewsProvider(redis_client_mock)


@pytest.fixture(name='iter_dict_from_bq_query_with_progress_mock', autouse=True)
def _iter_dict_from_bq_query_with_progress_mock() -> Iterator[MagicMock]:
    with patch.object(
        provider_module,
        'iter_dict_from_bq_query_with_progress'
    ) as mock:
        yield mock


class TestNonArticlePageViewsProvider:
    def test_should_always_return_empty_periods(
        self,
        non_article_page_views_provider: NonArticlePageViewsProvider,
        redis_client_get_mock: MagicMock
    ):
        redis_client_get_mock.return_value = None
        response = non_article_page_views_provider.get_page_views_by_content_type(
            content_type='blog-article',
            content_id=CONTENT_ID_1
        )
        assert response == {
            'totalPeriods': 0,
            'totalValue': ANY,
            'periods': []
        }

    def test_should_return_zero_total_value_if_not_in_redis(
        self,
        non_article_page_views_provider: NonArticlePageViewsProvider,
        redis_client_get_mock: MagicMock
    ):
        redis_client_get_mock.return_value = None
        response = non_article_page_views_provider.get_page_views_by_content_type(
            content_type='blog-article',
            content_id=CONTENT_ID_1
        )
        assert response['totalValue'] == 0

    def test_should_return_non_article_page_views_value_from_redis(
        self,
        non_article_page_views_provider: NonArticlePageViewsProvider,
        redis_client_get_mock: MagicMock
    ):
        redis_client_get_mock.return_value = '123'
        response = non_article_page_views_provider.get_page_views_by_content_type(
            content_type=CONTENT_TYPE_1,
            content_id=CONTENT_ID_1
        )
        assert response['totalValue'] == 123
        redis_client_get_mock.assert_called_once_with(
            f'non-article:{CONTENT_TYPE_1}:{CONTENT_ID_1}:page_views'
        )

    def test_should_put_page_view_total_in_redis(
        self,
        iter_dict_from_bq_query_with_progress_mock: MagicMock,
        non_article_page_views_provider: NonArticlePageViewsProvider,
        redis_client_set_mock: MagicMock
    ):
        iter_dict_from_bq_query_with_progress_mock.return_value = iter([{
            'content_type': CONTENT_TYPE_1,
            'content_id': CONTENT_ID_1,
            'page_view_count': 123
        }])
        non_article_page_views_provider.refresh_non_article_page_view_totals()
        iter_dict_from_bq_query_with_progress_mock.assert_called_with(
            project_name=non_article_page_views_provider.gcp_project_name,
            query=non_article_page_views_provider.non_article_page_view_totals_query,
            desc=ANY
        )
        redis_client_set_mock.assert_called_once_with(
            f'non-article:{CONTENT_TYPE_1}:{CONTENT_ID_1}:page_views',
            123
        )
