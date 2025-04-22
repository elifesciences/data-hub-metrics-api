import logging


LOGGER = logging.getLogger(__name__)


def main():
    LOGGER.info('Updating redis (dummy implementation)...')


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
