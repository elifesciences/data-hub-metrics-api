import logging

from data_hub_metrics_api.main import get_redis_client
from data_hub_metrics_api.non_article_page_views_provider import NonArticlePageViewsProvider

LOGGER = logging.getLogger(__name__)


def main():
    redis_client = get_redis_client()
    non_article_page_views_provider = NonArticlePageViewsProvider(redis_client)
    non_article_page_views_provider.refresh_non_article_page_view_totals()


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    main()
