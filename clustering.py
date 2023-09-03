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
import pickle, json
from pyspark.ml import Pipeline

#--------------------------------------- MASCHINEN ----------------------------------------------

# defines column headers for loaded date
cols = (
    'Name',
    'Typ',
    'DurchsatzProStunde',
    'Werkstoff',
    'Werkzeuge',
    'Bearbeitungsart'
)

# Create PySpark SparkSession
spark = SparkSession.builder \
    .master("local[1]") \
    .appName("SparkByExamples.com") \
    .getOrCreate()

# load data without headers
sparkDF = spark.read.options(inferSchema='True',delimiter=',', header='true').csv('trainingsdaten_maschinen_10000.csv')

# Create PySpark DataFrame from Pandas
#sparkDF=spark.createDataFrame(data) 
sparkDF = sparkDF.withColumn("DurchsatzProStunde",sparkDF["DurchsatzProStunde"].cast(FloatType()))

# Define the features
features = [
    'Name' ,
    'Typ',
    'DurchsatzProStunde',
    'Werkstoff',
    'Werkzeuge',
    'Bearbeitungsart'
]

# Define the StringIndexer and OneHotEncoder for categorical columns
indexers = [StringIndexer(inputCol=col, outputCol=col+"_index") for col in ["Name", "Typ", "Werkstoff", "Werkzeuge", "Bearbeitungsart"]]
encoders = [OneHotEncoder(inputCol=col+"_index", outputCol=col+"_onehot") for col in ["Name", "Typ", "Werkstoff", "Werkzeuge", "Bearbeitungsart"]]

# Create the Pipeline to apply transformations in sequence
pipeline_stages = indexers + encoders

pipeline = Pipeline(stages=pipeline_stages)
indexed_data = pipeline.fit(sparkDF).transform(sparkDF)


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

# Register the custom function as a UDF - with different weights (from 0.00001 to 5.0)
durchsatz_udf = udf(lambda vector: multiply_int(vector, 0.0001), returnType=FloatType())
werkstoff_udf = udf(lambda vector: multiply_sparse_vector(vector, 3.0), returnType=VectorUDT())
werkzeug_udf = udf(lambda vector: multiply_sparse_vector(vector, 2.0), returnType=VectorUDT())
typ_udf = udf(lambda vector: multiply_sparse_vector(vector, 5.0), returnType=VectorUDT())
art_udf = udf(lambda vector: multiply_sparse_vector(vector, 4.0), returnType=VectorUDT())

indexed_data = indexed_data.withColumn('DurchsatzProStunde', durchsatz_udf(indexed_data['DurchsatzProStunde']))
indexed_data = indexed_data.withColumn('Werkstoff_onehot', werkstoff_udf(indexed_data['Werkstoff_onehot']))
indexed_data = indexed_data.withColumn('Werkzeuge_onehot', werkzeug_udf(indexed_data['Werkzeuge_onehot']))
indexed_data = indexed_data.withColumn('Typ_onehot', typ_udf(indexed_data['Typ_onehot']))
indexed_data = indexed_data.withColumn('Bearbeitungsart_onehot', art_udf(indexed_data['Bearbeitungsart_onehot']))

# Combine the one-hot encoded vectors with other numeric and array columns
assembler = VectorAssembler(inputCols=["DurchsatzProStunde", "Name_onehot", "Typ_onehot", "Werkstoff_onehot", "Werkzeuge_onehot", "Bearbeitungsart_onehot"],
                            outputCol="features")
final_data = assembler.transform(indexed_data)

# Trains a k-means model.
kmeans = KMeans().setK(20).setSeed(1)
model_machine = kmeans.fit(final_data)
# Make predictions
predictions_machine = model_machine.transform(final_data)
# Evaluate clustering by computing Silhouette score
evaluator = ClusteringEvaluator()
silhouette = evaluator.evaluate(predictions_machine)
print("Silhouette with squared euclidean distance = " + str(silhouette))

# save trained model:
# model_machine.write().format("json").save("PATH/model_machine")

# save results - Assuming 'predictions' contains the clustered data with the predictions column
# predictions.write.parquet('path to hadoop HDFS.parquet')

# Show all entries of a specific cluster (e.g., cluster 0)
specific_cluster = predictions_machine.filter(predictions_machine["prediction"] == 1)
specific_cluster.show(truncate=False)


#--------------------------------------- SERVICES ----------------------------------------------

# defines column headers for loaded date
cols = (
    'Name',
    'Hersteller',
    'Funktion'
)

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

# Register the custom function as a UDF - with different weights (from 0.5 to 1.5)
name_udf = udf(lambda vector: multiply_sparse_vector(vector, 2.0), returnType=VectorUDT())
hersteller_udf = udf(lambda vector: multiply_sparse_vector(vector, 1.0), returnType=VectorUDT())
funktionen_udf = udf(lambda vector: multiply_sparse_vector(vector, 2.0), returnType=VectorUDT())

indexed_data = indexed_data.withColumn('Name_onehot', name_udf(indexed_data['Name_onehot']))
indexed_data = indexed_data.withColumn('Hersteller_onehot', hersteller_udf(indexed_data['Hersteller_onehot']))
indexed_data = indexed_data.withColumn('Funktion_onehot', funktionen_udf(indexed_data['Funktion_onehot']))

# Combine the one-hot encoded vectors with other numeric and array columns
assembler = VectorAssembler(inputCols=["Name_onehot", "Hersteller_onehot", "Funktion_onehot"],
                            outputCol="features")
final_data = assembler.transform(indexed_data)

# Trains a k-means model.
kmeans = KMeans().setK(16).setSeed(1)
model_service = kmeans.fit(final_data)
# Make predictions
predictions_service = model_service.transform(final_data)
# Evaluate clustering by computing Silhouette score
evaluator = ClusteringEvaluator()
silhouette = evaluator.evaluate(predictions_service)
print("Silhouette with squared euclidean distance = " + str(silhouette))

# save trained model:
# Serialize and save the model to a file
# model_service.write().format("json").save("PATH/model_service")

# save results - Assuming 'predictions' contains the clustered data with the predictions column
# predictions.write.parquet('path to hadoop HDFS.parquet')

# Show all entries of a specific cluster (e.g., cluster 0)
specific_cluster = predictions_service.filter(predictions_service["prediction"] == 0)
specific_cluster.show(truncate=False)


#--------------------------------------- FAKTORBERECHNUNG ----------------------------------------------

# create table which contains the cluster number and the factors
# as pandas dataframe, for local storage later on
pd_combi = pd.read_csv('trainingsdaten_kombination_10000.csv', header=0)

#convert predictions into pandas for storage and better search
pd_pred_machine = predictions_machine.toPandas()
pd_pred_service = predictions_service.toPandas()

pd_pred_machine.to_csv('.\predictions_machine.csv', index=False)
pd_pred_service.to_csv('.\predictions_service.csv', index=False)

# calculate the factor means between each collection of the same cluster number combination

# merge combination list to add columns for the machine cluster predicitons and service cluster predicitons
result_clustering = pd.merge(pd_combi, pd_pred_machine[['Name','prediction']], left_on="Name_Maschine", right_on="Name", sort=False).drop(columns = ['Name'])
result_clustering.rename(columns={"prediction": "Prediction_Maschine"}, inplace=True)

result_clustering = pd.merge(result_clustering, pd_pred_service[['Name','prediction']], left_on="Name_Service", right_on="Name", sort=False).drop(columns = ['Name'])
result_clustering.rename(columns={"prediction": "Prediction_Service"}, inplace=True)

result_clustering.to_csv('result_clustering_10000.csv')

# create dataframe to save mean values of calculation
num_m_cluster = 20
num_s_cluster = 16
pd_cluster_mean = pd.DataFrame({"Cluster_Maschine": [], 
                                "Cluster_Service": [],
                                "AbsatzmengeFaktor_mean": [], 
                                "PersonalkostenFaktor_mean": [], 
                                "EnergiekostenFaktor_mean": [], 
                                "ReparaturkostenProStueckFaktor_mean": [],
                                "MaterialkostenFaktor_mean": [],
                                "WartungskostenFaktor_mean": [],
                                "AbsatzpreisFaktor_mean": []})

for i in range(num_m_cluster):
    for k in range (num_s_cluster):
      
      # select all combinations with Cluster combinations, calculate the means and write a line of that cluster combinations into a new dataframe - ineffective right now
      AbsatzmengeFaktor_mean = result_clustering.loc[(result_clustering["Prediction_Maschine"] == i) & (result_clustering["Prediction_Service"] == k)]["AbsatzmengeFaktor"].mean()
      PersonalkostenFaktor_mean = result_clustering.loc[(result_clustering["Prediction_Maschine"] == i) & (result_clustering["Prediction_Service"] == k)]["PersonalkostenFaktor"].mean()
      EnergiekostenFaktor_mean = result_clustering.loc[(result_clustering["Prediction_Maschine"] == i) & (result_clustering["Prediction_Service"] == k)]["EnergiekostenFaktor"].mean()
      ReparaturkostenProStueckFaktor_mean = result_clustering.loc[(result_clustering["Prediction_Maschine"] == i) & (result_clustering["Prediction_Service"] == k)]["ReparaturkostenProStueckFaktor"].mean()
      MaterialkostenFaktor_mean = result_clustering.loc[(result_clustering["Prediction_Maschine"] == i) & (result_clustering["Prediction_Service"] == k)]["MaterialkostenFaktor"].mean()
      WartungskostenFaktor = result_clustering.loc[(result_clustering["Prediction_Maschine"] == i) & (result_clustering["Prediction_Service"] == k)]["WartungskostenFaktor"].mean()
      AbsatzpreisFaktor = result_clustering.loc[(result_clustering["Prediction_Maschine"] == i) & (result_clustering["Prediction_Service"] == k)]["AbsatzpreisFaktor"].mean()

      new_row = {'Cluster_Maschine':i, 
                 'Cluster_Service':k, 
                 "AbsatzmengeFaktor_mean": AbsatzmengeFaktor_mean, 
                 "PersonalkostenFaktor_mean": PersonalkostenFaktor_mean, 
                 "EnergiekostenFaktor_mean": EnergiekostenFaktor_mean, 
                 "ReparaturkostenProStueckFaktor_mean": ReparaturkostenProStueckFaktor_mean,
                 "MaterialkostenFaktor_mean": MaterialkostenFaktor_mean,
                 "WartungskostenFaktor_mean": WartungskostenFaktor,
                 "AbsatzpreisFaktor_mean": AbsatzpreisFaktor}
      
      pd_cluster_mean.loc[len(pd_cluster_mean)] = new_row

example_maschines = pd.DataFrame(pd_pred_machine.loc[(pd_pred_machine["Name"] == "Trumpf TruLaser 1030 fiber")])
example_maschines = pd.concat([example_maschines, pd_pred_machine.loc[(pd_pred_machine["Name"] == "DMG MORI DMP 70")]], ignore_index=True)
example_maschines = pd.concat([example_maschines, pd_pred_machine.loc[(pd_pred_machine["Name"] == "Heidelberg Speedmaster CX 104")]], ignore_index=True)
example_services = pd.DataFrame(pd_pred_service.loc[(pd_pred_service["Name"] == "Safety Tracker")])
example_services = pd.concat([example_services, pd_pred_service.loc[(pd_pred_service["Name"] == "Digital Manual")]], ignore_index=True)
example_services = pd.concat([example_services, pd_pred_service.loc[(pd_pred_service["Name"] == "Movement Optimization")]], ignore_index=True)

# save the results in csv
pd_cluster_mean.to_csv('means_clustering_10000.csv')
example_maschines.to_csv('example_maschines.csv')
example_services.to_csv('example_services.csv')