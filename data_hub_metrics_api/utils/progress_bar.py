from typing import Iterable, TypeVar
from tqdm import tqdm

T = TypeVar('T')


def iter_with_progress(data: Iterable[T], total: int, desc: str) -> Iterable[dict]:
    return tqdm(data, total=total, desc=desc)
