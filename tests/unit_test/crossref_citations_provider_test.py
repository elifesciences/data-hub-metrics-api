from typing import Iterable, Mapping
from data_hub_metrics_api.crossref_citations_provider import (
    get_citation_counts_by_article_id_and_version_map
)


class TestGetCitationCountsByArticleIdAndVersionMap:
    def test_should_return_map_for_valid_data(self):
        bq_result = [
            {'article_id': '12345', 'version_number': '1', 'citation_count': 10},
        ]
        expected_result = {
            ('12345', '1'): 10,
        }
        result = get_citation_counts_by_article_id_and_version_map(bq_result)
        assert result == expected_result

    def test_should_return_empty_dict_for_empty_list(self):
        bq_result: Iterable[dict] = []
        expected_result: Mapping[tuple[str, str], int] = {}
        result = get_citation_counts_by_article_id_and_version_map(bq_result)
        assert result == expected_result

    def test_should_create_map_entry_for_article_id_with_none_version_number(self):
        bq_result = [
            {'article_id': '12345', 'citation_count': 81, 'version_number': None}
        ]
        expected_result = {('12345', None): 81}
        result = get_citation_counts_by_article_id_and_version_map(bq_result)
        assert result == expected_result


class TestCrossrefCitationsProvider:
    def test_happy_path(self):
        pass
