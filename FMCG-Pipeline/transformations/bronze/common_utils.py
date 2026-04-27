from pyspark.sql.functions import current_timestamp, lit

def clean_columns(df):
    return df.toDF(*[
        c.strip().replace("-", "_").replace(" ", "_")
        for c in df.columns
    ])

def add_metadata(df, source_file):
    return df.withColumn("_ingest_ts", current_timestamp()) \
             .withColumn("_source_file", lit(source_file))