
# FMCG_PROJECT


🚀 FMCG data pipeline — clean, testable, and easy to extend

![Hero](diagrams/hero.svg)

TL;DR: A compact ETL + KPI studio that ingests raw sales data, applies business transformations, and produces consumer-ready KPI tables and CSVs for dashboards and downstream analytics.

Badges
- [![Python](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/)
- [![Docs](https://img.shields.io/badge/docs-ready-brightgreen)](docs)
- [![Screenshots](https://img.shields.io/badge/gallery-5%20images-purple)](dashboards/screenshots)

What you'll find here
- A clean Bronze → Silver → Gold pipeline layout in `src/`.
- KPI scripts that write consumer-ready CSVs to `outputs/`.
- A small gallery showing sample dashboards and KPI visualizations.

Why use this repo
- Focused: single-responsibility scripts for easy testing.
- Composable: drop-in transforms and KPIs; swap storage and orchestration layers.
- Portable: runs locally or in any cloud orchestration environment.

--

**High-level overview**

FMCG_PROJECT is an end-to-end ETL and KPI generation repository that turns transactional and master-data inputs (orders, payments, products, customers, order items) into clean analytics artifacts and KPI summaries for business consumers.

Core pipeline stages
- Bronze (raw ingestion): `src/bronze/` — scripts that fetch or read raw input files and land them into a raw zone.
- Silver (transformations): `src/silver/` — business-rule transforms, deduplication, enrichment, and quarantining.
- Gold (analytics/KPIs): `src/gold/` — KPI extraction, aggregation and final datasets consumed by dashboards and reports.

Data outputs (examples)
- [outputs/sales_summary.csv](outputs/sales_summary.csv) — aggregated sales snapshot.
- [outputs/sku_performance.csv](outputs/sku_performance.csv) — SKU-level performance indicators.


Example (preview of `outputs/sales_summary.csv`)

| date       | total_orders | total_sales | avg_order_value |
|------------|--------------:|-----------:|----------------:|
| 2026-05-01 |           124 |   54,321.00 |          438.07 |
| 2026-05-02 |           139 |   62,105.50 |          446.80 |
| 2026-05-03 |           110 |   48,900.00 |          444.55 |


Screenshots / quick gallery

<table>
	<tr>
		<td><img src="dashboards/screenshots/distributor_perf.png" alt="Distributor" width="420"></td>
		<td><img src="dashboards/screenshots/sales_trend.png" alt="Sales trend" width="420"></td>
	</tr>
	<tr>
		<td><img src="dashboards/screenshots/sku_performance.png" alt="SKU perf" width="420"></td>
		<td><img src="dashboards/screenshots/stock_aging.png" alt="Stock aging" width="420"></td>
	</tr>
</table>

Tip: The screenshots are examples — replace them with your BI exports for live dashboards.


Architecture diagram (pipeline)

```mermaid
flowchart LR
	subgraph Ingest
		A[Raw sources \nCSV/DB/APIs] --> B[src/bronze]
	end
	B --> C[Bronze zone (raw store)]
	C --> D[src/silver]\n(Transform & enrich)
	D --> E[Silver zone (cleaned tables)]
	E --> F[src/gold]\n(KPIs & aggregations)
	F --> G[Gold zone (analytics tables) / outputs/]
	G --> H[Consumers: dashboards, reports, ML]
```

Architecture notes
- The codebase is intentionally modular: each script focuses on one source or one KPI.
- The pipeline can be executed locally (Python scripts) or orchestrated using any scheduler (Airflow, Prefect, Azure Data Factory).
- Storage formats: the design favors columnar formats (Parquet) and CSVs for small outputs; swap in your cloud storage as needed.

File map (quick)
- [src/bronze/ingest_customers.py](src/bronze/ingest_customers.py) — ingest customers
- [src/bronze/ingest_orders.py](src/bronze/ingest_orders.py) — ingest orders
- [src/bronze/ingest_order_items.py](src/bronze/ingest_order_items.py) — ingest order-item level detail
- [src/bronze/ingest_payments.py](src/bronze/ingest_payments.py) — ingest payments and receipts
- [src/bronze/ingest_products.py](src/bronze/ingest_products.py) — ingest products master
- [src/silver/transform_customers.py](src/silver/transform_customers.py) — canonicalize customers
- [src/silver/transform_products.py](src/silver/transform_products.py) — canonicalize products
- [src/silver/transform_sales.py](src/silver/transform_sales.py) — sales cleaning & joins
- [src/silver/quarantine_sales.py](src/silver/quarantine_sales.py) — rules for quarantining bad rows
- [src/gold/kpi_sales_summary.py](src/gold/kpi_sales_summary.py) — high-level sales KPIs
- [src/gold/kpi_sku_performance.py](src/gold/kpi_sku_performance.py) — SKU-level KPIs
- [src/gold/kpi_distributor_performance.py](src/gold/kpi_distributor_performance.py) — distributor KPIs
- [src/gold/kpi_stock_aging.py](src/gold/kpi_stock_aging.py) — stock aging analysis
- [docs/pipeline_flow.md](docs/pipeline_flow.md) — pipeline flow documentation
- [docs/kpi_definitions.md](docs/kpi_definitions.md) — KPI definitions and formulas
- [docs/governance.md](docs/governance.md) — governance and data ownership

Getting started (developer quickstart)

1) Create and activate a Python virtual environment

```bash
python -m venv .venv
.\
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate
```

2) Install dependencies

The repository does not lock dependencies to a single file; suggested packages are listed below. Add them to `requirements.txt` for reproducibility.

```bash
pip install pandas pyarrow fastparquet sqlalchemy click pyyaml
pip install -r requirements.txt  # if you populate it
```

3) Run a Bronze ingest (example)

```bash
python src/bronze/ingest_orders.py --input-path inputs/orders.csv --output-path bronze/orders.parquet
```

4) Run Silver transforms

```bash
python src/silver/transform_sales.py --bronze-path bronze --silver-path silver
```

5) Generate Gold KPIs

```bash
python src/gold/kpi_sales_summary.py --silver-path silver --output outputs/sales_summary.csv
```

If your scripts use a CLI different than the examples above, inspect the script docstrings or open the `src/*` files to discover exact arguments.

Data contracts and outputs
- Raw inputs should be placed into a consistent `inputs/` layout (one file per source). The `bronze/`, `silver/` and `gold/` folders mirror storage zones.
- Output artifacts in `outputs/` are consumer-ready CSVs.

Design decisions & best practices
- Idempotency: all pipeline stages are designed to be re-run safely by overwriting zone-specific paths.
- Observability: add logging and metrics around each script for execution time and row counts.
- Testing: add unit tests for transformation functions (prefer pytest) and lightweight integration tests that run transforms on a small sample dataset.

Extending the project
- Add a new raw source: create `src/bronze/ingest_<source>.py`, document inputs in `docs/`, and add a transform in `src/silver/`.
- Add a new KPI: create `src/gold/kpi_<name>.py` that reads from the `silver` zone and writes to `outputs/`.

Governance & documentation
- Authoritative KPI definitions live in [docs/kpi_definitions.md](docs/kpi_definitions.md).
- Data ownership, retention, and lineage notes belong in [docs/governance.md](docs/governance.md).

Roadmap & next steps
- Populate `requirements.txt` with pinned versions.
- Add automated CI to run linters and pytest.
- Add containerized execution (Dockerfile + Compose) and an orchestration DAG for scheduling.
- Export architecture diagrams as PNG/SVG under `diagrams/` for easy inclusion in docs.

Contributing
- Fork, branch, add tests, and open a PR with clear changelog entries. Include sample inputs for integration tests.

License & authors
- Add a `LICENSE` file to declare project license (MIT/Apache-2.0 recommended).
- Maintain `AUTHORS.md` or use Git history for contributor attribution.

Contact / Questions
- Open an issue or reach out to the maintainer(s) listed in repository metadata.

--

If you'd like, I can:
- populate `requirements.txt` with a tested list of packages and pins,
- render and export the mermaid architecture diagram to PNG/SVG and add it to `diagrams/`, or
- update individual scripts to add CLI flags and improved logging.

Enjoy — this README is designed to be both an executive-level overview and a developer playbook for running and extending the FMCG pipeline.
