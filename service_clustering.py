from pyspark.ml.evaluation import ClusteringEvaluator
from pyspark.ml.clustering import KMeans, KMeansModel, GaussianMixture
from pyspark.ml.feature import StringIndexer, OneHotEncoder, VectorAssembler, StandardScaler
from pyspark.ml.linalg import Vectors, SparseVector, VectorUDT
from numpy import array
from math import sqrt
import pandas as pd
import numpy as np

# used for creatingthe  datafraame and dataset
from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, FloatType, ArrayType
from pyspark.sql.functions import col, udf, split, when , lit
import pickle
from pyspark.ml import Pipeline

# defines column headers for loaded date
cols = (
    'Name',
    'Hersteller',
    'Funktion'
)

# Create PySpark SparkSession
spark = SparkSession.builder \
    .master("local[1]") \
    .appName("SparkByExamples.com") \
    .getOrCreate()

# spark.conf.set("spark.executor.instances", "10")  # Change the number of instances as needed
# Example of increasing memory allocation (adjust values as needed)
# spark.conf.set("spark.driver.memory", "8g")
# spark.conf.set("spark.executor.memory", "16g")

# load data without headers
sparkDF = spark.read.options(inferSchema='True',delimiter=',', header='true').csv('trainingsdaten_services_10000.csv')

# Define the features
features = [
    'Name' ,
    'Hersteller',
    'Funktion'
]

# Define the StringIndexer and OneHotEncoder for categorical columns
indexers = [StringIndexer(inputCol=col, outputCol=col+"_index") for col in ["Name", "Hersteller", "Funktion"]]
encoders = [OneHotEncoder(inputCol=col+"_index", outputCol=col+"_onehot") for col in ["Name", "Hersteller", "Funktion"]]

# Create the Pipeline to apply transformations in sequence
pipeline_stages = indexers + encoders

pipeline = Pipeline(stages=pipeline_stages)
indexed_data = pipeline.fit(sparkDF).transform(sparkDF)
indexed_data.show()

# Use scaling to give different features different weights
# Custom function to perform element-wise multiplication with a scalar
def multiply_sparse_vector(sparse_vector, scalar):
    # Multiply non-zero elements by the scalar, leave zero elements unchanged
    values = [v * scalar if v != 0.0 else v for v in sparse_vector.values]
    return SparseVector(sparse_vector.size, sparse_vector.indices, values)

# Custom function to perform element-wise multiplication with a scalar
def multiply_int(input, scalar):
    # Multiply non-zero elements by the scalar, leave zero elements unchanged
    return input * scalar

# Register the custom function as a UDF - with different weights (from 0.5 to 1.5)
name_udf = udf(lambda vector: multiply_sparse_vector(vector, 1.0), returnType=VectorUDT())
hersteller_udf = udf(lambda vector: multiply_sparse_vector(vector, 0.5), returnType=VectorUDT())
funktionen_udf = udf(lambda vector: multiply_sparse_vector(vector, 1.5), returnType=VectorUDT())

indexed_data = indexed_data.withColumn('Name_onehot', name_udf(indexed_data['Name_onehot']))
indexed_data = indexed_data.withColumn('Hersteller_onehot', hersteller_udf(indexed_data['Hersteller_onehot']))
indexed_data = indexed_data.withColumn('Funktion_onehot', funktionen_udf(indexed_data['Funktion_onehot']))

# Combine the one-hot encoded vectors with other numeric and array columns
assembler = VectorAssembler(inputCols=["Name_onehot", "Hersteller_onehot", "Funktion_onehot"],
                            outputCol="features")
final_data = assembler.transform(indexed_data)

# Show the final data
final_data.show(truncate=False)


# No need for scales data, since features are weight before
# scaler = StandardScaler(inputCol="features", outputCol="scaledFeatures",
#                         withStd=True, withMean=False)
# # Compute summary statistics by fitting the StandardScaler
# scalerModel = scaler.fit(final_data)
# # Normalize each feature to have unit standard deviation.
# scaledData = scalerModel.transform(final_data)
# scaledData.show(truncate=False)


# Trains a k-means model.
kmeans = KMeans().setK(16).setSeed(1)
model = kmeans.fit(final_data)
# Make predictions
predictions = model.transform(final_data)
# Evaluate clustering by computing Silhouette score
evaluator = ClusteringEvaluator()
silhouette = evaluator.evaluate(predictions)
print("Silhouette with squared euclidean distance = " + str(silhouette))

# Shows the result.
# print("Cluster Centers: ")
# ctr=[]
# centers = model.clusterCenters()
# for center in centers:
#   ctr.append(center)
#   print(center)

# save results - Assuming 'predictions' contains the clustered data with the predictions column
# predictions.write.parquet('path to hadoop HDFS.parquet')

# Show all entries of a specific cluster (e.g., cluster 0)
specific_cluster = predictions.filter(predictions["prediction"] == 0)
specific_cluster.show(truncate=False)

specific_cluster = predictions.filter(predictions["prediction"] == 2)
specific_cluster.show(truncate=False)
specific_cluster = predictions.filter(predictions["prediction"] == 3)
specific_cluster.show(truncate=False)
specific_cluster = predictions.filter(predictions["prediction"] == 4)
specific_cluster.show(truncate=False)



# -----------------------------------------------
# SIMPLE DATA EXAMPLE

# # Beispiel-Datenframe
# data2 = spark.createDataFrame([
#     (1, ["Fräsen", "Bohren"]),
#     (2, ["Drehen"]),
#     (3, ["Fräsen"]),
#     (4, ["Schneiden", "Bohren"]),
#     (5, ["Schneiden", "Drehen"])
# ], ["ID", "Bearbeitungsart"])

# # Convert "Bearbeitungsart" from string array to string (concatenate the array elements)
# data2 = data2.withColumn("Bearbeitungsart", data2["Bearbeitungsart"].cast("string"))

# # Use StringIndexer to convert the "Bearbeitungsart" string to numeric indices
# indexer = StringIndexer(inputCol="Bearbeitungsart", outputCol="BearbeitungsartIndex")
# indexed_data = indexer.fit(data2).transform(data2)

# # Use OneHotEncoder to convert the numeric indices to one-hot encoded vectors
# encoder = OneHotEncoder(inputCols=["BearbeitungsartIndex"], outputCols=["BearbeitungsartOneHot"])
# encoded_data = encoder.fit(indexed_data).transform(indexed_data)

# # Use VectorAssembler to create the feature vector
# assembler = VectorAssembler(inputCols=["ID", "BearbeitungsartOneHot"], outputCol="features")
# final_data = assembler.transform(encoded_data)

# # Show the final data
# final_data.show(truncate=False)
