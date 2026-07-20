# Sales Data Platform

An end-to-end data engineering case study for retail sales analytics. The pipeline stages transactional data in a PostgreSQL-compatible warehouse, builds a store-performance mart, publishes the result to ClickHouse, and exposes it to BI tools such as Apache Superset.

The original case study was completed during a Sapiens Solutions Greenplum course. This repository is an extended and cleaned-up portfolio version: source code is organized, sample data is synthetic, the local environment is reproducible, and the core mart logic is covered by automated tests.

## Business goal

Create one analytical mart for comparing store performance across a selected period:

- gross and net revenue;
- discounts;
- sold quantity and receipt count;
- visitor traffic and conversion rate;
- promotional share;
- average items per receipt;
- average receipt and revenue per visitor.

The field previously called `profit` is named `net_revenue` here. Revenue after discounts is not accounting profit and should not be presented as such.

## Architecture

```text
CSV dimensions ───────┐
                      ├── PostgreSQL / Greenplum ── store mart ── ClickHouse ── Superset
transactional source ─┘             ▲
                                    │
                              Apache Airflow
```

The production-oriented design targets Greenplum:

- dimensions are replicated;
- large facts are distributed on join keys;
- facts are partitioned by date;
- incremental loads replace only affected partitions;
- ClickHouse acts as the low-latency serving layer.

The local demo uses PostgreSQL because it is lightweight and compatible with the portable mart query. Greenplum-specific DDL and design notes are kept separately under `sql/greenplum/`.

![Original Airflow DAG](docs/original-airflow-dag.png)

## Repository structure

```text
.
├── dags/                         # Airflow orchestration example
├── docs/                         # Architecture, ERD, and dashboard evidence
├── sample_data/                  # Small synthetic dataset
├── sales_pipeline/               # Reusable pipeline runner
├── sql/
│   ├── marts/                    # Portable analytical query
│   ├── postgres/                 # Reproducible local schema
│   └── greenplum/                # Target MPP design
├── tests/                        # Mart and configuration tests
├── docker-compose.yml
└── pyproject.toml
```

## Quick start

Requirements: Docker with Compose.

```bash
docker compose up --build --abort-on-container-exit pipeline
```

The command:

1. creates the PostgreSQL source and warehouse tables;
2. loads synthetic CSV data;
3. builds `sales.mart_store_performance`;
4. publishes the mart to ClickHouse;
5. prints row counts and validation totals.

Inspect the mart in PostgreSQL:

```bash
docker compose exec postgres psql -U sales -d sales -c \
  "select * from sales.mart_store_performance order by plant"
```

Inspect the ClickHouse serving table:

```bash
docker compose exec clickhouse clickhouse-client --query \
  "select * from sales.mart_store_performance order by plant format PrettyCompact"
```

Stop and remove local containers:

```bash
docker compose down -v
```

## Pipeline commands

The same runner can execute stages independently:

```bash
python -m sales_pipeline init
python -m sales_pipeline mart
python -m sales_pipeline publish
python -m sales_pipeline all
```

Connection settings are read from environment variables. See `.env.example`.

## Data model

Facts:

- `bills_head`: receipt header and transaction date;
- `bills_item`: receipt lines, quantities, and gross amounts;
- `traffic`: visitors per store and day;
- `coupons`: applied promotion per item.

Dimensions:

- `stores`;
- `promos`;
- `promo_types`.

![Entity relationship diagram](docs/erd.png)

## Mart calculation

The portable query in `sql/marts/store_performance.sql` is used by the local PostgreSQL runner and by DuckDB-based tests. The query deliberately uses `LEFT JOIN` from stores to aggregates so stores are not silently removed when traffic or promotions are absent.

Discount rules in the synthetic example:

- type `001`: fixed discount amount;
- type `002`: percentage of unit price;
- one discount per `coupon_id`, selected deterministically with `row_number()`.

The test suite verifies revenue, discounts, receipt counts, traffic conversion, promotional share, and zero/empty edge cases.

## Airflow orchestration

`dags/sales_pipeline.py` shows three explicit stages:

1. initialize and load sources;
2. build and validate the warehouse mart;
3. publish the serving table to ClickHouse.

The DAG calls the same package used by Docker and local execution, avoiding a second implementation hidden inside Airflow operators.

## Greenplum design

`sql/greenplum/001_schema.sql` documents the target MPP layout:

- co-location of `bills_head` and `bills_item` on `billnum`;
- replicated small dimensions;
- monthly range partitions for date-based fact access;
- append-optimized column storage for analytical facts and marts.

The local PostgreSQL schema does not pretend to reproduce Greenplum distribution behavior. It exists to validate transformations and make the project runnable without a multi-node cluster.

## Data quality

The pipeline validates:

- uniqueness of business keys;
- non-negative quantities, revenue, traffic, and discounts;
- referential integrity between receipts and receipt lines;
- uniqueness of the mart grain (`plant`);
- reconciliation of mart revenue against source receipt lines;
- valid conversion and promotional-rate ranges.

Validation failures stop the pipeline before publication.

## Development

```bash
python -m venv .venv
.venv/Scripts/activate
python -m pip install -e ".[dev]"
pytest
ruff check .
ruff format --check .
```

CI runs the same checks on every push and pull request.

## Evidence and limitations

The diagrams and dashboard screenshot under `docs/` come from the original course environment. That managed environment is not distributed with this repository. The included source data is synthetic and contains no company or customer data.

![Superset dashboard from the original environment](docs/superset-dashboard.png)

This project demonstrates data modeling, SQL transformations, orchestration boundaries, MPP design decisions, validation, and a serving-layer pattern. It is not a benchmark of Greenplum or ClickHouse performance.
