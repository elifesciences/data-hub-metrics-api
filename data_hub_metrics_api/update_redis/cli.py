import logging

from data_hub_metrics_api.main import get_citations_provider_list

LOGGER = logging.getLogger(__name__)


def main():
    citations_provider_list = get_citations_provider_list()
    for provider in citations_provider_list:
        provider.refresh_data()
    LOGGER.info('Updating redis (dummy implementation)...')


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
