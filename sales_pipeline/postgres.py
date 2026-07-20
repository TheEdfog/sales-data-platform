from __future__ import annotations

import csv
from pathlib import Path

import psycopg

from sales_pipeline.config import Settings

TABLES = (
    "stores",
    "promo_types",
    "promos",
    "bills_head",
    "bills_item",
    "traffic",
    "coupons",
)


def _execute_file(connection: psycopg.Connection, path: Path) -> None:
    connection.execute(path.read_text(encoding="utf-8"))


def initialize(settings: Settings) -> None:
    schema_path = settings.project_root / "sql" / "postgres" / "001_schema.sql"
    data_dir = settings.project_root / "sample_data"

    with psycopg.connect(settings.postgres_dsn) as connection:
        _execute_file(connection, schema_path)
        for table in TABLES:
            csv_path = data_dir / f"{table}.csv"
            with csv_path.open(encoding="utf-8", newline="") as source:
                reader = csv.reader(source)
                columns = next(reader)
                connection.execute(f"truncate table sales.{table} cascade")
                column_list = ", ".join(columns)
                with connection.cursor().copy(
                    f"copy sales.{table} ({column_list}) from stdin with (format csv)"
                ) as copy:
                    for row in reader:
                        copy.write_row(row)


def build_mart(settings: Settings) -> int:
    query_path = settings.project_root / "sql" / "marts" / "store_performance.sql"
    query = query_path.read_text(encoding="utf-8")

    with psycopg.connect(settings.postgres_dsn) as connection:
        connection.execute("drop table if exists sales.mart_store_performance")
        connection.execute(f"create table sales.mart_store_performance as {query}")
        connection.execute("alter table sales.mart_store_performance add primary key (plant)")
        validate_mart(connection)
        return connection.execute("select count(*) from sales.mart_store_performance").fetchone()[0]


def validate_mart(connection: psycopg.Connection) -> None:
    checks = {
        "duplicate mart grain": """
            select count(*) from (
                select plant from sales.mart_store_performance
                group by plant having count(*) > 1
            ) duplicates
        """,
        "negative measures": """
            select count(*) from sales.mart_store_performance
            where gross_revenue < 0 or discount < 0 or sold_quantity < 0 or traffic < 0
        """,
        "invalid rates": """
            select count(*) from sales.mart_store_performance
            where promo_rate_pct not between 0 and 100
               or conversion_rate_pct not between 0 and 100
        """,
        "revenue reconciliation": """
            select case when
                (select coalesce(sum(gross_revenue), 0) from sales.mart_store_performance)
                = (select coalesce(sum(rpa_sat), 0) from sales.bills_item)
            then 0 else 1 end
        """,
    }
    for name, query in checks.items():
        failures = connection.execute(query).fetchone()[0]
        if failures:
            raise RuntimeError(f"data quality check failed: {name} ({failures} rows)")


def fetch_mart(settings: Settings) -> tuple[list[str], list[tuple]]:
    with psycopg.connect(settings.postgres_dsn) as connection:
        cursor = connection.execute("select * from sales.mart_store_performance order by plant")
        columns = [description.name for description in cursor.description]
        return columns, cursor.fetchall()
