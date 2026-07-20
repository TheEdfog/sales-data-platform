from __future__ import annotations

import argparse

from sales_pipeline.clickhouse import publish
from sales_pipeline.config import Settings
from sales_pipeline.postgres import build_mart, fetch_mart, initialize


def run_stage(stage: str, settings: Settings) -> None:
    if stage in {"init", "all"}:
        initialize(settings)
        print("source and warehouse tables initialized")

    if stage in {"mart", "all"}:
        row_count = build_mart(settings)
        print(f"mart built and validated: {row_count} rows")

    if stage in {"publish", "all"}:
        columns, rows = fetch_mart(settings)
        row_count = publish(settings, columns, rows)
        print(f"ClickHouse serving table published: {row_count} rows")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the retail sales data pipeline")
    parser.add_argument(
        "stage", choices=["init", "mart", "publish", "all"], nargs="?", default="all"
    )
    args = parser.parse_args()
    run_stage(args.stage, Settings.from_environment())
