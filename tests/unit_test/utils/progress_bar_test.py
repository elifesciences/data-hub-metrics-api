from data_hub_metrics_api.utils.progress_bar import iter_with_progress


def test_should_return_all_items():
    data = [1, 2, 3, 4, 5]
    total = len(data)
    desc = "Test Progress"

    result = list(iter_with_progress(data, total, desc))
    assert result == data
