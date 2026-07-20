from pathlib import Path

import duckdb
import pytest

ROOT = Path(__file__).resolve().parents[1]

TABLES = (
    "stores",
    "promo_types",
    "promos",
    "bills_head",
    "bills_item",
    "traffic",
    "coupons",
)


@pytest.fixture
def mart_rows() -> tuple[dict[str, tuple], list[str]]:
    connection = duckdb.connect()
    connection.execute("create schema sales")
    for table in TABLES:
        csv_path = (ROOT / "sample_data" / f"{table}.csv").as_posix()
        connection.execute(
            f"create table sales.{table} as select * from read_csv_auto('{csv_path}')"
        )
    query = (ROOT / "sql" / "marts" / "store_performance.sql").read_text(encoding="utf-8")
    result = connection.execute(query)
    columns = [description[0] for description in result.description]
    return {row[0]: tuple(row) for row in result.fetchall()}, columns


def test_store_mart_metrics(mart_rows: tuple[dict[str, tuple], list[str]]) -> None:
    rows, columns = mart_rows
    m001 = dict(zip(columns, rows["M001"], strict=True))
    m002 = dict(zip(columns, rows["M002"], strict=True))

    assert float(m001["gross_revenue"]) == 230.0
    assert float(m001["discount"]) == 20.0
    assert float(m001["net_revenue"]) == 210.0
    assert m001["bills_count"] == 2
    assert float(m001["conversion_rate_pct"]) == 10.0

    assert float(m002["gross_revenue"]) == 200.0
    assert float(m002["discount"]) == 10.0
    assert float(m002["net_revenue"]) == 190.0


def test_store_without_sales_is_preserved(
    mart_rows: tuple[dict[str, tuple], list[str]],
) -> None:
    rows, columns = mart_rows
    m003 = dict(zip(columns, rows["M003"], strict=True))

    assert float(m003["gross_revenue"]) == 0.0
    assert m003["bills_count"] == 0
    assert float(m003["conversion_rate_pct"]) == 0.0
