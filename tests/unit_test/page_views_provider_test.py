import pytest

from data_hub_metrics_api.page_views_provider import PageViewsProvider


@pytest.fixture(name='page_views_provider')
def _page_views_provider() -> PageViewsProvider:
    return PageViewsProvider()


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
