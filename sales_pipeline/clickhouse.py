from __future__ import annotations

import clickhouse_connect

from sales_pipeline.config import Settings


def publish(settings: Settings, columns: list[str], rows: list[tuple]) -> int:
    client = clickhouse_connect.get_client(
        host=settings.clickhouse_host,
        port=settings.clickhouse_port,
        username=settings.clickhouse_user,
        password=settings.clickhouse_password,
    )
    client.command("create database if not exists sales")
    client.command(
        """
        create table if not exists sales.mart_store_performance
        (
            plant String,
            store_name String,
            gross_revenue Decimal(18, 2),
            discount Decimal(18, 2),
            net_revenue Decimal(18, 2),
            sold_quantity Int64,
            bills_count Int64,
            traffic Int64,
            promo_sold Int64,
            promo_rate_pct Decimal(8, 2),
            avg_items_per_bill Decimal(18, 2),
            conversion_rate_pct Decimal(8, 2),
            avg_bill_amount Decimal(18, 2),
            revenue_per_visitor Decimal(18, 2)
        )
        engine = MergeTree
        order by plant
        """
    )
    client.command("truncate table sales.mart_store_performance")
    client.insert("sales.mart_store_performance", rows, column_names=columns)
    return len(rows)
