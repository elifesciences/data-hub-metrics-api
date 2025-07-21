import os.path
from pathlib import Path


SQL_DIR = os.path.dirname(__file__)


def get_sql_path(sql_filename: str) -> str:
    return os.path.join(SQL_DIR, sql_filename)


def get_sql_query_from_file(sql_filename: str) -> str:
    return Path(get_sql_path(sql_filename)).read_text(encoding='utf-8')
