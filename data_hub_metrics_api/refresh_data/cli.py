import logging

from data_hub_metrics_api.main import get_citations_provider_list, get_redis_client

LOGGER = logging.getLogger(__name__)


def main():
    citations_provider_list = get_citations_provider_list(get_redis_client())
    LOGGER.info('Refreshing data from BigQuery...')
    for provider in citations_provider_list:
        provider.refresh_data()
    LOGGER.info('Refreshing data from BigQuery completed.')


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
