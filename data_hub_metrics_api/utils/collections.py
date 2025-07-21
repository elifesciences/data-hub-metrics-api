from collections import deque
from itertools import islice
from typing import Iterable, TypeVar


T = TypeVar('T')


def chain_queue_and_iterable(queue: deque, iterable):
    while queue:
        yield queue.popleft()
    yield from iterable


def iter_batch_iterable(
    iterable: Iterable[T],
    batch_size: int
) -> Iterable[Iterable[T]]:
    iterator = iter(iterable)
    while True:
        batch_iterable = islice(iterator, batch_size)
        try:
            peeked_value_queue: deque[T] = deque()
            peeked_value_queue.append(next(batch_iterable))
            # by using and consuming a queue we are allowing the memory
            # for the peeked value to be released
            batch_iterable = chain_queue_and_iterable(peeked_value_queue, batch_iterable)
        except StopIteration:
            # reached end, avoid yielding an empty iterable
            return
        yield batch_iterable
