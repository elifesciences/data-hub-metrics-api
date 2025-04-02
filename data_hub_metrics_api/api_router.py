from fastapi import APIRouter

from data_hub_metrics_api.api_router_typing import CitationsResponseSequence


EXAMPLE_CITATIONS_RESPONSE: CitationsResponseSequence = [
    {
        "service": "Crossref",
        "uri": "https://doi.org/10.7554/eLife.85111.2",
        "citations": 7
    },
    {
        "service": "PubMed Central",
        "uri": "",
        "citations": 0
    },
    {
        "service": "Scopus",
        "uri": "",
        "citations": 0
    }
]


def create_api_router() -> APIRouter:
    router = APIRouter()

    @router.get('/elife-metrics/article/85111/citations/version/2')
    def provide_citations() -> CitationsResponseSequence:
        return EXAMPLE_CITATIONS_RESPONSE

    return router
