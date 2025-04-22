from data_hub_metrics_api.update_redis.cli import main


class TestMain:
    def test_should_not_fail(self):
        main()
