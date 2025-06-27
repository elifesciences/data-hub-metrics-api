import argparse
import logging
from typing import Optional, Sequence

from data_hub_metrics_api.main import get_redis_client
from data_hub_metrics_api.page_views_and_downloads_provider import PageViewsAndDownloadsProvider

LOGGER = logging.getLogger(__name__)


def parse_args(vargs: Optional[Sequence[str]]) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument('--number-of-months', type=int)
    return parser.parse_args(vargs)


def main(vargs: Optional[Sequence[str]] = None):
    args = parse_args(vargs)
    redis_client = get_redis_client()
    page_views_and_downloads_provider = PageViewsAndDownloadsProvider(redis_client)
    page_views_and_downloads_provider.refresh_page_views_monthly(
        number_of_months=args.number_of_months
    )


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
