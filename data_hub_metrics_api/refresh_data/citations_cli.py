import logging

from data_hub_metrics_api.crossref_citations_provider import CrossrefCitationsProvider
from data_hub_metrics_api.main import get_citations_provider_list, get_redis_client

LOGGER = logging.getLogger(__name__)


def main():
    redis_client = get_redis_client()
    crossref_citations_provider = CrossrefCitationsProvider(
        name="Crossref",
        redis_client=redis_client
    )
    citations_provider_list = get_citations_provider_list(crossref_citations_provider)
    LOGGER.info('Refreshing data from BigQuery...')
    for provider in citations_provider_list:
        provider.refresh_data()
    LOGGER.info('Refreshing data from BigQuery completed.')


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
