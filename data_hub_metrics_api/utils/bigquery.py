import logging
from typing import Any, Iterable, Optional, Sequence

from google.cloud import bigquery
from google.cloud.bigquery.table import RowIterator

from data_hub_metrics_api.utils.progress_bar import iter_with_progress

LOGGER = logging.getLogger(__name__)


def get_bq_client(project_name: str) -> bigquery.Client:
    return bigquery.Client(project=project_name)


def get_bq_result_from_bq_query(
    project_name: str,
    query: str,
    query_parameters: Optional[Sequence[Any]] = tuple()
) -> RowIterator:
    client = get_bq_client(project_name=project_name)
    job_config = bigquery.QueryJobConfig(query_parameters=query_parameters)
    query_job = client.query(query, job_config=job_config)  # Make an API request.
    bq_result = query_job.result()  # Waits for query to finish
    LOGGER.debug('bq_result: %r', bq_result)
    return bq_result


def iter_dict_from_bq_query(
    project_name: str,
    query: str,
    query_parameters: Optional[Sequence[Any]] = tuple()
) -> Iterable[dict]:
    bq_result = get_bq_result_from_bq_query(
        project_name=project_name,
        query=query,
        query_parameters=query_parameters
    )
    LOGGER.info('Total rows from BigQuery %d', bq_result.total_rows)
    for row in bq_result:
        LOGGER.debug('row: %r', row)
        yield dict(row.items())


def iter_dict_from_bq_query_with_progress(
    project_name: str,
    query: str,
    desc: str = 'Loading'
) -> Iterable[dict]:
    bq_result = get_bq_result_from_bq_query(
        project_name=project_name,
        query=query
    )
    total_rows: int = bq_result.total_rows  # type: ignore
    LOGGER.info('Total rows from BigQuery: %d', total_rows)
    for row in iter_with_progress(bq_result, total=total_rows, desc=desc):
        LOGGER.debug('row: %r', row)
        yield dict(row.items())
