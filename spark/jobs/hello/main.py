from pyspark.sql import SparkSession

spark = SparkSession.builder.getOrCreate()
dataframe = spark.read.json('s3a://orders/*')
average = dataframe.agg({'amount': 'avg'})
average.write.mode("OVERWRITE").json('s3a://results/orders/average')