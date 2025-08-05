import logging
from datetime import datetime

from cassandra.auth import PlainTextAuthProvider
from cassandra.cluster import Cluster
from pyspark.sql import SparkSession, functions as F, types as T

import platform
LOCALLY = False

def create_keyspace(session):
    session.execute("""
        CREATE KEYSPACE IF NOT EXISTS spark_streams
        WITH REPLICATION = {'class': 'SimpleStrategy', 'replication_factor': '1'};                
    """)
    
    print ("Keyspace 'spark_streams' created successfully.")
    
def create_table(session):
    session.execute("""
        CREATE TABLE IF NOT EXISTS spark_streams.users_created (
            id UUID PRIMARY KEY,
            first_name TEXT,
            last_name TEXT,
            gender TEXT,
            address TEXT,
            postcode TEXT,
            email TEXT,
            username TEXT,
            dob TEXT,
            registered_data TEXT,
            phone TEXT,
            picture TEXT
        );
    """)
    print ("Table 'users_created' created successfully.")
    
def insert_data(session, **kwargs):
    id = kwargs.get('id')
    first_name = kwargs.get('first_name')
    last_name = kwargs.get('last_name')
    gender = kwargs.get('gender')
    address = kwargs.get('address')
    postcode = kwargs.get('postcode')
    email = kwargs.get('email')
    username = kwargs.get('username')
    dob = kwargs.get('dob')
    registered_data = kwargs.get('registered_data')
    phone = kwargs.get('phone')
    picture = kwargs.get('picture')
    
    try:
        session.execute("""
            INSERT INTO spark_streams.users_created (id,first_name,last_name,gender,address,postcode,email,username,dob,registered_data,phone,picture)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);
        """, (id, first_name, last_name, gender, address, postcode, email, username, dob, registered_data, phone, picture))
        logging.info("Data inserted into Cassandra successfully.")
    except Exception as e:
        logging.error(f"Error inserting data into Cassandra: {e}")
        return
    
    print ("Data inserted successfully.")

def create_spark_connection():
    s_conn = None
    try:
        # import glob
        # s_conn = SparkSession.builder \
        #     .appName('SparkDataStreaming') \
        #     .config("spark.jars", ",".join(glob.glob("jars/*.jar"))) \
        #     .config('spark.cassandra.connection.host', 'localhost') \
        #     .getOrCreate()
        s_conn = SparkSession.builder \
            .appName('SparkDataStreaming') \
            .config('spark.jars.packages', "com.datastax.spark:spark-cassandra-connector_2.12:3.5.1,"
                    "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.1") \
            .config('spark.cassandra.connection.host', 'localhost') \
            .getOrCreate()
        logging.info("Spark session created successfully.")
    except Exception as e:
        logging.error(f"Error creating Spark session: {e}")
        # raise e
    
    return s_conn

def connect_to_kafka(spark_conn):
    spark_df = None
    try:
        if True:
            spark_df = spark_conn.readStream \
                .format("kafka") \
                .option("kafka.bootstrap.servers", "localhost:9092") \
                .option("subscribe", "users_created") \
                .option("startingOffsets", "earliest") \
                .load()
        else:
            spark_df = spark_conn.readStream \
                .format("kafka") \
                .option("kafka.bootstrap.servers", "broker:29092") \
                .option("subscribe", "users_created") \
                .option("startingOffsets", "earliest") \
                .load()
        logging.info("Connected to Kafka topic 'users_created' successfully.")
    except Exception as e:
        logging.error(f"Error connecting to Kafka topic: {e}")
        raise e
    
    return spark_df

def create_cassandra_connection():
    session = None
    try:
        cluster = Cluster(['localhost'])
        session = cluster.connect()
    except Exception as e:
        logging.error(f"Error connecting to Cassandra: {e}")
        # raise e
    return session

def create_selection_df_from_kafka(spark_df):
    schema = T.StructType([
        T.StructField("id", T.StringType(), nullable=False),
        T.StructField("first_name", T.StringType(), nullable=False),
        T.StructField("last_name", T.StringType(), nullable=False),
        T.StructField("gender", T.StringType(), nullable=False),
        T.StructField("address", T.StringType(), nullable=False),
        T.StructField("postcode", T.StringType(), nullable=False),
        T.StructField("email", T.StringType(), nullable=False),
        T.StructField("username", T.StringType(), nullable=False),
        T.StructField("dob", T.StringType(), nullable=False),
        T.StructField("registered_data", T.StringType(), nullable=False),
        T.StructField("phone", T.StringType(), nullable=False),
        T.StructField("picture", T.StringType(), nullable=False),
    ])
    res = spark_df.selectExpr("CAST(value AS STRING)") \
        .select(F.from_json(F.col("value"), schema).alias("data")).select("data.*") \
        .withColumn("id", F.expr("uuid()"))
    print ('spark_df selection applied: ', res)
    return res

if __name__ == "__main__":
    spark_conn = create_spark_connection()
    
    if spark_conn:
        spark_df = connect_to_kafka(spark_conn)
        selected_df = create_selection_df_from_kafka(spark_df)
        cass_ss = create_cassandra_connection()
        
        if cass_ss:
            create_keyspace(cass_ss)
            create_table(cass_ss)
            if LOCALLY: exit(0)  # For development, exit after creating keyspace and table

            logging.info("Streaming is being started...")

            streaming_query = (selected_df.writeStream.format("org.apache.spark.sql.cassandra")
                                .option('checkpointLocation', '/tmp/checkpoint')
                                .option('keyspace', 'spark_streams')
                                .option('table', 'users_created')
                                .start())

            streaming_query.awaitTermination()