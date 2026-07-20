from __future__ import annotations

from datetime import datetime

from airflow import DAG
from airflow.operators.bash import BashOperator

with DAG(
    dag_id="sales_data_platform",
    description="Build and publish the retail store-performance mart",
    start_date=datetime(2025, 1, 1),
    schedule="0 5 * * *",
    catchup=False,
    max_active_runs=1,
    tags=["data-engineering", "greenplum", "clickhouse"],
) as dag:
    initialize_sources = BashOperator(
        task_id="initialize_sources",
        bash_command="python -m sales_pipeline init",
    )
    build_and_validate_mart = BashOperator(
        task_id="build_and_validate_mart",
        bash_command="python -m sales_pipeline mart",
    )
    publish_to_clickhouse = BashOperator(
        task_id="publish_to_clickhouse",
        bash_command="python -m sales_pipeline publish",
    )

    initialize_sources >> build_and_validate_mart >> publish_to_clickhouse
