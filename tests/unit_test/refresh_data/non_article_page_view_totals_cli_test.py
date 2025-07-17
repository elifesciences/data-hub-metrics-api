from typing import Iterator
from unittest.mock import MagicMock, patch

import pytest

from data_hub_metrics_api.refresh_data.non_article_page_view_totals_cli import main
import data_hub_metrics_api.refresh_data.non_article_page_view_totals_cli as cli_module


@pytest.fixture(name="non_article_page_views_provider_class_mock", autouse=True)
def _non_article_page_views_provider_class_mock() -> Iterator[MagicMock]:
    with patch.object(cli_module, "NonArticlePageViewsProvider") as mock:
        yield mock


@pytest.fixture(name="non_article_page_views_provider_mock")
def _non_article_page_views_provider_mock(
    non_article_page_views_provider_class_mock: MagicMock
) -> MagicMock:
    return non_article_page_views_provider_class_mock.return_value


class TestMain:
    def test_should_call_refresh_page_view_and_download_totals_on_the_provider(
        self,
        non_article_page_views_provider_mock: MagicMock,
    ):
        main()
        (
            non_article_page_views_provider_mock
            .refresh_non_article_page_view_totals
            .assert_called_with()
        )
