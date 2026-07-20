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

TABLE_DEFINITIONS = {
    "stores": "plant varchar, store_name varchar",
    "promo_types": "type_id varchar, description varchar",
    "promos": "promo_id varchar, material varchar, type_id varchar, discount decimal(18, 2)",
    "bills_head": "billnum varchar, plant varchar, calday date",
    "bills_item": "billnum varchar, material varchar, rpa_sat decimal(18, 2), qty bigint",
    "traffic": "plant varchar, traffic_date date, quantity bigint",
    "coupons": (
        "coupon_id varchar, plant varchar, billnum varchar, material varchar, "
        "promo_id varchar, coupon_date date"
    ),
}


@pytest.fixture
def mart_rows() -> tuple[dict[str, tuple], list[str]]:
    connection = duckdb.connect()
    connection.execute("create schema sales")
    for table in TABLES:
        csv_path = (ROOT / "sample_data" / f"{table}.csv").as_posix()
        connection.execute(f"create table sales.{table} ({TABLE_DEFINITIONS[table]})")
        connection.execute(f"copy sales.{table} from '{csv_path}' (header true)")
    connection.execute("insert into sales.stores values ('M999', 'Test store without facts')")
    query = (ROOT / "sql" / "marts" / "store_performance.sql").read_text(encoding="utf-8")
    result = connection.execute(query)
    columns = [description[0] for description in result.description]
    return {row[0]: tuple(row) for row in result.fetchall()}, columns


def test_store_mart_metrics(mart_rows: tuple[dict[str, tuple], list[str]]) -> None:
    rows, columns = mart_rows
    m001 = dict(zip(columns, rows["M001"], strict=True))

    assert len(rows) == 16
    assert float(m001["gross_revenue"]) > 0
    assert float(m001["discount"]) > 0
    assert float(m001["net_revenue"]) == pytest.approx(
        float(m001["gross_revenue"]) - float(m001["discount"]), abs=0.01
    )
    assert m001["bills_count"] > 0
    assert 0 < float(m001["conversion_rate_pct"]) <= 100


def test_store_without_sales_is_preserved(
    mart_rows: tuple[dict[str, tuple], list[str]],
) -> None:
    rows, columns = mart_rows
    empty_store = dict(zip(columns, rows["M999"], strict=True))

    assert float(empty_store["gross_revenue"]) == 0.0
    assert empty_store["bills_count"] == 0
    assert float(empty_store["conversion_rate_pct"]) == 0.0
