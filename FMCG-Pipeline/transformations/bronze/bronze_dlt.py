import dlt
from pyspark.sql.types import *
from pyspark.sql.functions import col, lit, current_timestamp
from common_utils import clean_columns


# =========================
# METADATA FUNCTION (STRONG VERSION)
# =========================
def add_metadata(df, source_file):
    return df.withColumn("_ingest_ts", current_timestamp()) \
             .withColumn("_source_file", lit(source_file)) \
             .withColumn("_batch_id", lit("batch_001"))


# =========================
# SCHEMAS
# =========================
customers_schema = StructType([
    StructField("customer_id", StringType(), True),
    StructField("customer_unique_id", StringType(), True),
    StructField("customer_zip_code_prefix", IntegerType(), True),
    StructField("customer_city", StringType(), True),
    StructField("customer_state", StringType(), True)
])

orders_schema = StructType([
    StructField("order_id", StringType(), True),
    StructField("customer_id", StringType(), True),
    StructField("order_status", StringType(), True),
    StructField("order_purchase_timestamp", TimestampType(), True),
    StructField("order_approved_at", TimestampType(), True),
    StructField("order_delivered_carrier_date", TimestampType(), True),
    StructField("order_delivered_customer_date", TimestampType(), True),
    StructField("order_estimated_delivery_date", TimestampType(), True)
])

order_items_schema = StructType([
    StructField("order_id", StringType(), True),
    StructField("order_item_id", IntegerType(), True),
    StructField("product_id", StringType(), True),
    StructField("seller_id", StringType(), True),
    StructField("shipping_limit_date", TimestampType(), True),
    StructField("price", DoubleType(), True),
    StructField("freight_value", DoubleType(), True)
])

payments_schema = StructType([
    StructField("order_id", StringType(), True),
    StructField("payment_sequential", IntegerType(), True),
    StructField("payment_type", StringType(), True),
    StructField("payment_installments", IntegerType(), True),
    StructField("payment_value", DoubleType(), True)
])

products_schema = StructType([
    StructField("product_id", StringType(), True),
    StructField("product_category_name", StringType(), True)
])

sellers_schema = StructType([
    StructField("seller_id", StringType(), True),
    StructField("seller_zip_code_prefix", IntegerType(), True),
    StructField("seller_city", StringType(), True),
    StructField("seller_state", StringType(), True)
])


# =========================
# CUSTOMERS
# =========================
@dlt.view
def customers_source():
    return clean_columns(
        spark.read.format("csv")
        .option("header", "true")
        .schema(customers_schema)
        .load("/Volumes/fmcg/bronze/customers/customers_raw.csv")
    )


@dlt.table(name="customers_raw", table_properties={"quality": "bronze"})
def customers_raw():
    df = dlt.read("customers_source")

    return add_metadata(
        df.filter(col("customer_id").isNotNull()).dropDuplicates(),
        "customers_raw.csv"
    )


@dlt.table(name="customers_quarantine", table_properties={"quality": "bronze_quarantine"})
def customers_quarantine():
    df = dlt.read("customers_source")

    return add_metadata(
        df.filter(col("customer_id").isNull())
          .withColumn("failure_reason", lit("customer_id_null")),
        "customers_raw.csv"
    )


# =========================
# ORDERS
# =========================
@dlt.view
def orders_source():
    return clean_columns(
        spark.read.format("csv")
        .option("header", "true")
        .schema(orders_schema)
        .load("/Volumes/fmcg/bronze/orders/orders_raw.csv")
    )


@dlt.table(name="orders_raw", table_properties={"quality": "bronze"})
@dlt.expect("valid_order_id", "order_id IS NOT NULL")
def orders_raw():
    df = dlt.read("orders_source")

    return add_metadata(
        df.filter(
            col("order_id").isNotNull() &
            col("customer_id").isNotNull() &
            col("order_purchase_timestamp").isNotNull()
        ).dropDuplicates(),
        "orders_raw.csv"
    )


@dlt.table(name="orders_quarantine", table_properties={"quality": "bronze_quarantine"})
def orders_quarantine():
    df = dlt.read("orders_source")

    return add_metadata(
        df.filter(
            col("order_id").isNull() |
            col("customer_id").isNull()
        ).withColumn("failure_reason", lit("invalid_order_record")),
        "orders_raw.csv"
    )


# =========================
# ORDER ITEMS
# =========================
@dlt.view
def order_items_source():
    return clean_columns(
        spark.read.format("csv")
        .option("header", "true")
        .schema(order_items_schema)
        .load("/Volumes/fmcg/bronze/order_items/order_items_raw.csv")
    )


@dlt.table(name="order_items_raw", table_properties={"quality": "bronze"})
def order_items_raw():
    df = dlt.read("order_items_source")

    return add_metadata(
        df.filter(
            col("order_id").isNotNull() &
            col("product_id").isNotNull() &
            col("seller_id").isNotNull() &
            (col("price") > 0)
        ).dropDuplicates(),
        "order_items_raw.csv"
    )


@dlt.table(name="order_items_quarantine", table_properties={"quality": "bronze_quarantine"})
def order_items_quarantine():
    df = dlt.read("order_items_source")

    return add_metadata(
        df.filter(
            col("order_id").isNull() |
            col("product_id").isNull() |
            col("seller_id").isNull() |
            (col("price") <= 0)
        ).withColumn("failure_reason", lit("invalid_order_item")),
        "order_items_raw.csv"
    )


# =========================
# PAYMENTS
# =========================
@dlt.view
def payments_source():
    return clean_columns(
        spark.read.format("csv")
        .option("header", "true")
        .schema(payments_schema)
        .load("/Volumes/fmcg/bronze/payments/order_payments_raw.csv")
    )


@dlt.table(name="payments_raw", table_properties={"quality": "bronze"})
def payments_raw():
    df = dlt.read("payments_source")

    return add_metadata(
        df.filter(
            col("order_id").isNotNull() &
            (col("payment_value") > 0)
        ).dropDuplicates(),
        "order_payments_raw.csv"
    )


@dlt.table(name="payments_quarantine", table_properties={"quality": "bronze_quarantine"})
def payments_quarantine():
    df = dlt.read("payments_source")

    return add_metadata(
        df.filter(
            col("order_id").isNull() |
            (col("payment_value") <= 0)
        ).withColumn("failure_reason", lit("invalid_payment")),
        "order_payments_raw.csv"
    )


# =========================
# PRODUCTS
# =========================
@dlt.view
def products_source():
    return clean_columns(
        spark.read.format("csv")
        .option("header", "true")
        .schema(products_schema)
        .load("/Volumes/fmcg/bronze/products/products_raw.csv")
    )


@dlt.table(name="products_raw", table_properties={"quality": "bronze"})
def products_raw():
    df = dlt.read("products_source")

    return add_metadata(
        df.filter(col("product_id").isNotNull()).dropDuplicates(),
        "products_raw.csv"
    )


@dlt.table(name="products_quarantine", table_properties={"quality": "bronze_quarantine"})
def products_quarantine():
    df = dlt.read("products_source")

    return add_metadata(
        df.filter(col("product_id").isNull())
          .withColumn("failure_reason", lit("product_id_null")),
        "products_raw.csv"
    )


# =========================
# SELLERS
# =========================
@dlt.view
def sellers_source():
    return clean_columns(
        spark.read.format("csv")
        .option("header", "true")
        .schema(sellers_schema)
        .load("/Volumes/fmcg/bronze/seller/sellers_raw.csv")
    )


@dlt.table(name="sellers_raw", table_properties={"quality": "bronze"})
def sellers_raw():
    df = dlt.read("sellers_source")

    return add_metadata(
        df.filter(col("seller_id").isNotNull()).dropDuplicates(),
        "sellers_raw.csv"
    )


@dlt.table(name="sellers_quarantine", table_properties={"quality": "bronze_quarantine"})
def sellers_quarantine():
    df = dlt.read("sellers_source")

    return add_metadata(
        df.filter(col("seller_id").isNull())
          .withColumn("failure_reason", lit("seller_id_null")),
        "sellers_raw.csv"
    )