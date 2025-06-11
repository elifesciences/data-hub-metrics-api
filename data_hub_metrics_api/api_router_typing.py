from typing import Sequence, TypedDict


class CitationsSourceMetricTypedDict(TypedDict):
    service: str
    uri: str
    citations: int


CitationsResponseSequence = Sequence[CitationsSourceMetricTypedDict]


class MetricTimePeriodItemTypedDict(TypedDict):
    period: str  # either 'YYYY-MM' or 'YYYY-MM-DD'
    value: int


class MetricTimePeriodResponseTypedDict(TypedDict):
    totalPeriods: int
    totalValue: int
    periods: Sequence[MetricTimePeriodItemTypedDict]
