from sales_pipeline.config import Settings


def test_defaults_are_suitable_for_local_development() -> None:
    settings = Settings()
    assert settings.postgres_host == "localhost"
    assert settings.postgres_db == "sales"
    assert settings.clickhouse_port == 8123
    assert "password=sales" in settings.postgres_dsn
