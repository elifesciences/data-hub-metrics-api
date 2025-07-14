from typing import Literal, Sequence, TypedDict


ContentTypeLiteral = Literal[
    'blog-article',
    'labs-post',
    'collection',
    'digest',
    'event',
    'interview',
    'press-package'
]


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


class MetricSummaryItemTypedDict(TypedDict):
    id: int
    views: int
    downloads: int
    crossref: int
    pubmed: int
    scopus: int


class MetricSummaryResponseTypedDict(TypedDict):
    total: int
    items: Sequence[MetricSummaryItemTypedDict]
