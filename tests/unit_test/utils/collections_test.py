from typing import Iterable, Sequence, TypeVar

from data_hub_metrics_api.utils.collections import (
    iter_batch_iterable
)

T = TypeVar('T')


def _to_list_of_batch_list(
    iterable_of_batch_iterable: Iterable[Iterable[T]]
) -> Sequence[Sequence[T]]:
    return [list(batch_iterable) for batch_iterable in iterable_of_batch_iterable]


class TestIterBatchIterable:
    def test_should_batch_list(self):
        assert _to_list_of_batch_list(iter_batch_iterable(
            [0, 1, 2, 3, 4],
            2
        )) == [[0, 1], [2, 3], [4]]

    def test_should_batch_iterable(self):
        assert _to_list_of_batch_list(iter_batch_iterable(
            iter([0, 1, 2, 3, 4]),
            2
        )) == [[0, 1], [2, 3], [4]]

    def test_should_not_yield_empty_iterable(self):
        assert _to_list_of_batch_list(iter_batch_iterable(
            iter([]),
            2
        )) == []
