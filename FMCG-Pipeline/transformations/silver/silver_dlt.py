import dlt
from pyspark.sql.functions import col, lower, upper, trim, to_date, lit, current_timestamp


# =========================
# RETAILER MASTER
# =========================
@dlt.table(name="silver_retailer_master", table_properties={"quality": "silver"})
def retailer_master():

    df = dlt.read("customers_raw")

    return df.select(
        col("customer_id").alias("retailer_id"),
        trim(lower(col("customer_city"))).alias("city"),
        trim(upper(col("customer_state"))).alias("region")
    ).dropDuplicates(["retailer_id"])


# =========================
# DISTRIBUTOR MASTER
# =========================
@dlt.table(name="silver_distributor_master", table_properties={"quality": "silver"})
def distributor_master():

    df = dlt.read("sellers_raw")

    return df.select(
        col("seller_id").alias("distributor_id"),
        trim(lower(col("seller_city"))).alias("city"),
        trim(upper(col("seller_state"))).alias("region")
    ).dropDuplicates(["distributor_id"])


# =========================
# SKU MASTER
# =========================
@dlt.table(name="silver_sku_master", table_properties={"quality": "silver"})
def sku_master():

    df = dlt.read("products_raw")

    return df.select(
        col("product_id").alias("sku_id"),
        trim(lower(col("product_category_name"))).alias("category")
    ).dropDuplicates(["sku_id"])


# =========================
# SALES TRANSACTIONS
# =========================
@dlt.table(name="silver_sales_transactions", table_properties={"quality": "silver"})
def sales_transactions():

    orders = dlt.read("orders_raw").drop("_ingest_ts", "_source_file", "_batch_id")
    items = dlt.read("order_items_raw").drop("_ingest_ts", "_source_file", "_batch_id")

    sales = orders.join(items, "order_id", "inner")

    # Strong validation (now correct)
    sales = sales.filter(
        (col("price") > 0) &
        col("order_id").isNotNull() &
        col("product_id").isNotNull() &
        col("seller_id").isNotNull() &
        col("order_purchase_timestamp").isNotNull()
    )

    # Master enrichment
    sales = sales \
        .join(dlt.read("silver_sku_master"), col("product_id") == col("sku_id"), "left") \
        .join(dlt.read("silver_distributor_master"), col("seller_id") == col("distributor_id"), "left") \
        .join(dlt.read("silver_retailer_master"), col("customer_id") == col("retailer_id"), "left")

    result = sales.select(
        col("order_id").alias("invoice_id"),
        col("seller_id").alias("distributor_id"),
        col("customer_id").alias("retailer_id"),
        col("product_id").alias("sku_id"),
        to_date("order_purchase_timestamp").alias("invoice_date"),
        lit(1).alias("quantity"),
        (col("price") + col("freight_value")).cast("decimal(18,2)").alias("gross_amount"),
        col("price").cast("decimal(18,2)").alias("net_amount"),
        (col("price")).cast("decimal(18,2)").alias("sales_value"),
        col("order_status").alias("channel"),
        current_timestamp().alias("processing_ts")
    )

    return result.dropDuplicates(["invoice_id", "sku_id"])


# =========================
# QUARANTINE SALES
# =========================
@dlt.table(name="silver_quarantine_sales", table_properties={"quality": "silver_quarantine"})
def quarantine_sales():

    orders = dlt.read("orders_raw").drop("_ingest_ts", "_source_file", "_batch_id")
    items = dlt.read("order_items_raw").drop("_ingest_ts", "_source_file", "_batch_id")

    sales = orders.join(items, "order_id", "inner")

    return sales.filter(
        (col("price") <= 0) |
        col("order_id").isNull() |
        col("product_id").isNull() |
        col("seller_id").isNull()
    ).withColumn(
        "failure_reason",
        lit("invalid_sales_record")
    )