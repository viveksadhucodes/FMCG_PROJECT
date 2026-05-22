
# KPI Definitions

## Purpose

This document defines the KPI contract for the FMCG pipeline. The repository currently contains bronze and silver processing logic, so the KPIs below are written against the curated silver transaction layer that the code already produces.

## KPI Design Principles

- Every KPI must trace back to a curated table.
- Every KPI must have a documented formula.
- Every KPI must be reproducible from source data and transformation code.
- Every KPI must specify the grain at which it is calculated.

## Source Tables Used For KPIs

- `silver_sales_transactions`
- `silver_retailer_master`
- `silver_distributor_master`
- `silver_sku_master`
- `silver_quarantine_sales`

## Current Analytical Fields Available

From `silver_sales_transactions`, the pipeline provides:

- `invoice_id`
- `distributor_id`
- `retailer_id`
- `sku_id`
- `invoice_date`
- `quantity`
- `gross_amount`
- `net_amount`
- `sales_value`
- `channel`
- `processing_ts`

## KPI Catalogue

| KPI Name | Definition | Formula | Grain | Source |
|---|---|---|---|---|
| Total Sales Value | Sum of sales value for the selected period | `SUM(sales_value)` | invoice line / period | `silver_sales_transactions` |
| Gross Revenue | Sum of gross amount including freight | `SUM(gross_amount)` | invoice line / period | `silver_sales_transactions` |
| Net Revenue | Sum of net amount excluding freight | `SUM(net_amount)` | invoice line / period | `silver_sales_transactions` |
| Total Quantity | Total units sold | `SUM(quantity)` | invoice line / period | `silver_sales_transactions` |
| Distinct Invoices | Number of unique invoices | `COUNT(DISTINCT invoice_id)` | period | `silver_sales_transactions` |
| Distinct Retailers | Number of active retailers in the period | `COUNT(DISTINCT retailer_id)` | period | `silver_sales_transactions` |
| Distinct Distributors | Number of active distributors in the period | `COUNT(DISTINCT distributor_id)` | period | `silver_sales_transactions` |
| Distinct SKUs | Number of active SKUs in the period | `COUNT(DISTINCT sku_id)` | period | `silver_sales_transactions` |
| Average Order Value | Average invoice value across distinct invoices | `SUM(sales_value) / COUNT(DISTINCT invoice_id)` | period | `silver_sales_transactions` |
| Average Line Value | Average value per sales row | `AVG(sales_value)` | invoice line / period | `silver_sales_transactions` |
| Quarantine Rate | Share of rejected sales rows | `COUNT(quarantine_rows) / (COUNT(valid_rows) + COUNT(quarantine_rows))` | run / period | `silver_quarantine_sales` + `silver_sales_transactions` |

## Recommended Business KPIs For Client Delivery

The repository does not yet include gold-layer implementation, but these are the most natural client-facing KPIs to build next:

### Sales performance

- day-over-day sales growth
- month-over-month sales growth
- average order value
- revenue by retailer region
- revenue by distributor

### Product performance

- top SKUs by revenue
- top SKUs by quantity
- category contribution to revenue
- SKU velocity over time

### Channel and customer performance

- sales by channel
- active retailer count
- repeat retailer count
- distributor coverage by region

### Data quality KPIs

- quarantine row count by source
- quarantine rate by source
- missing-key count by source
- duplicate row count after deduplication

## Business Rules Behind The Calculations

The silver code defines the following standard assumptions:

- each sales row currently has `quantity = 1`
- `gross_amount = price + freight_value`
- `net_amount = price`
- `sales_value = price`
- `invoice_date` is derived from `order_purchase_timestamp`
- duplicate rows are removed by `invoice_id` and `sku_id`

## KPI Reporting Requirements

For every future KPI implementation, the following must be documented:

1. business purpose
2. formula
3. source table
4. refresh frequency
5. owner
6. audience
7. expected tolerance or reconciliation rules

## Client Readiness Checklist

- confirm whether the KPI uses invoice-line grain or order grain
- confirm whether freight should be included in revenue reporting
- confirm the official currency and rounding rules
- confirm whether returns, cancellations, and refunds are in scope
- confirm whether quarantine rows should be excluded or reported separately

