from typing import Iterable
from tqdm import tqdm


def iter_with_progress(data: Iterable[dict], total: int, desc: str) -> Iterable[dict]:
    return tqdm(data, total=total, desc=desc)
