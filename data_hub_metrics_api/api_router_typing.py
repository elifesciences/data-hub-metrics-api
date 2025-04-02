from typing import Sequence, TypedDict


class CitationsSourceMetricTypedDict(TypedDict):
    service: str
    uri: str
    citations: int


CitationsResponseSequence = Sequence[CitationsSourceMetricTypedDict]
