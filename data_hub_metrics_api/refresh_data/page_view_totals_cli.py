import logging

from data_hub_metrics_api.main import get_redis_client
from data_hub_metrics_api.page_views_and_downloads_provider import PageViewsAndDownloadsProvider

LOGGER = logging.getLogger(__name__)


def main():
    redis_client = get_redis_client()
    page_views_and_downloads_provider = PageViewsAndDownloadsProvider(redis_client)
    page_views_and_downloads_provider.refresh_page_view_and_download_totals()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
