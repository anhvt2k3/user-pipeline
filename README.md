27/07 20:00
- create .venv
- install apache-airflow
- create the kafka_stream
- airflow only support Linux, so the env must be compatible to Linux
- recreate .venv
- trying auto activate env on creating terminal
- too messy, just use every time `source .venv/bin/activate`
- first run worked after 1 ad-hoc error
- doing the format, done it

28/07 16:00
- write the docker-compose for 1st service: zookeeper
- and 2nd service: kafka with confluent for a metric reporter
- 3rd service: schema registry
- 4rd service: control center
- control center will listen to the schema registry for the schema to make the visualization

- running `docker compose up -d`
- missing docker daemon from wsl
- using `echo 'export DOCKER_HOST=tcp://$(cat /etc/resolv.conf | grep nameserver | awk "{print \$2}"):2375' >> ~/.bashrc && source ~/.bashrc
` to set another host
- tried `unset docker`, it worked
- now undoing the whole auto thing with
```
# Remove old DOCKER_HOST setting
sed -i '/DOCKER_HOST/d' ~/.bashrc

# Add default local socket setting
echo 'export DOCKER_HOST=unix:///var/run/docker.sock' >> ~/.bashrc

# Reload shell config
source ~/.bashrc
```
- retrying `docker compose up -d`
- container broker is error
- gpt said that image should be 'cp-kafka' but it is 'cp-zookeeper' in the original project
- discovered some mistypes using DiffChecker
- now, chema-registry is down
- another typos, compared it to the origin config and fixed
- the host compose is online
- next compose will need re-compose
`
docker compose up -d
`

- going to `localhost:9021` for control-center
  - found this docs for all possible confluent stacks to manage Kafka `https://github.com/confluentinc/cp-all-in-one/blob/8.0.0-post/cp-all-in-one-community/docker-compose.yml`
- just found out that we're using 'cp-sever' = 'cp-kafka' + CP's features
- btw CP = Confluent Platform
- created a new docs for all the possible essential information `https://docs.google.com/document/d/1b_S07-Uz0RnirVdfd7Nsi7gBfiIvXP4RxbtOA4SbngA/edit?usp=sharing`
- just a reminder the running script should be `python dags/kafka_stream.py`
  
- trying to connect data stream to kafka once
  - making a connection
  - created a new topic 
  - close the connection
- `docker compose down` = opposite of `docker compose up` (stop the containers and remove all of them)

- added webserver for apache-airflow with a bunch of fields
- adding script/entrypoint: cmds to follow while intializing the webserver or the scheduler (airflow service)
- entrypoint:
  - `#!bin/bash` this should be executed using Bash shell
  - `set -e` rollback the moment one of them fail
  - `[ -e ... ]` if condition to check the existence of the file in ...
  - `!` is not
  - `-f` is applying `-e` AND it is a regular file (not a directory/link/...)
  - `$(command -v pip)` dynamically find `pip` and execute with the flag behind
  - `&&` conjunction to a command
  - `exec` conclude everything above then run this

- now we're ready for a compose up again
- teacher's worked, i failed despite his mistypo in entrypoint.sh dir
- got this `webserver-1      | exec /opt/airflow/script/entrypoint.sh: no such file or directory`
- doing this `sudo apt install dos2unix  # Ubuntu`, done with some stranges
- not fixing it
- mabe missing this to open its 'executibility' `chmod +x ./script/entrypoint.sh`
- composing down, mabe the latest yaml is not used // didnt help
- retried with connecting the folder only // not helping

- removing `version: '3'` since copilot said new Compose v2+ do not require
- copilot: problem is with non executable `script/entrypoint.sh`, need `chmod +x ...` for it
- copilot: serious typos in entrypoint.sh

- the tutorial skipping the making of `requirements.txt` file
- problem: airflow using 3.9 while auto created env is py3.10
- solution:
```
image: apache/airflow:2.6.0-python3.10
>> pip freeze > requirements.txt
```
- not helping

- just afraid that skipping finding out how to write this `requirements.txt` file will make this problem never be considered ever again
- mabe i should just deal with the error base on what the log said?

- final-solution: Airflow had everything it needs, only not-standard packages is needed in `requirements.txt` file (aka `kafka-python` at this point)
- also, entrypoint had some typos

- advanced options for automation:
```
# Remove any old requirements to avoid duplication
rm -f dags-requirements.txt plugins-requirements.txt merged-requirements.txt

# Generate pipreqs-based requirements for dags/
pipreqs ./dags --force --savepath dags-requirements.txt

# Generate pipreqs-based requirements for plugins/
pipreqs ./plugins --force --savepath plugins-requirements.txt

# Combine and deduplicate all requirements
cat dags-requirements.txt plugins-requirements.txt | sort | uniq > merged-requirements.txt

# (Optional) Rename it to requirements.txt if you want to mount into Airflow container
cp merged-requirements.txt requirements.txt
```

- bootstrap_servers is broker:29092, Producer produce in there and Kafka distribute the products 
- `stream_data()` activated (for today), get 1 data after DAG is activated again
- Airflow recognized that in its webserver
- you can make it execute manually using the switch button next to the DAG's name

- current Airflow configuration in `docker-compose` is inspired by its creator guide at `https://airflow.apache.org/docs/apache-airflow/3.0.3/docker-compose.yaml`
- creator guide is the general version make use of all the included components
- `<<`: spread the configuration stored in the previously set variable (line begin with `&`). Inherited configs can be overwrite on
- 1 Airflow image can run in many modes, setting `command` field will change this mode
- normally Airflow compose require `airflow-init` instance, but in this project those steps are cut off through manual setting up via `entrypoint.sh`
- Airflow must comes with a Postgres service too

- `stream_data()` is updated to stream data continuously in 1 minutes

- adding Spark as consumers, 1 worker - 1 master system
- more worker of the same config can be added by completely copy-paste the first worker (but *do change the service's name of the new workers*)
- spark-worker must have 1gb memory minimum

- Cassandra: a NoSQL db, using BigTable (not JSON like MongoDB).
- Data is in tables, no Joining support, only simple query included, usable mostly for Logging, IoT processing, Realtime apps.
- instead of working with tables, Cassandra works with key_space

- next step: writting code for Spark
- `pip install cassandra-driver spark pyspark`

- data fed by Kafka usually need further processing before storable in a db, they're sometimes sent in binary format
- in the future, for any example you can search `spark kafka example`, you shall get `https://spark.apache.org/docs/latest/streaming/structured-streaming-kafka-integration.html`

- at this point, we dont need Schema Registry (or Control Center) anymore

- run the code `spark_stream.py` to check its validity. Seeing this is good
```
Setting default log level to "WARN".
To adjust logging level use sc.setLogLevel(newLevel). For SparkR, use setLogLevel(newLevel).
```

- `pyspark` folder is disappearing from Explorer: something is wrong with Window in displaying directory from WSL
- Max Spark version that spark-cassandra-connector support currently is 3.5.1, while that is 4.0.0 for spark-kafka-connector (check `https://mvnrepository.com/`)
  - a jar name will be like this <package-name>_<scala-version>:<spark-version>
  - on the MVN Repo site, the Version column that all jar file has is Version of Spark that it supports
- Therefore, rollback Spark to 3.5.1 is crucial:
```
pip uninstall pyspark -y
pip install pyspark==3.5.1
```
- auto download from Spark is sometime unreliable: `.config('spark.jars.packages', "com.datastax.spark:spark-cassandra-connector_2.13:3.5.1,""org.apache.spark:spark-sql-kafka-0-10_2.13:4.0.0") \`
  - replaceable by manual download & use this line in SparkSession `.config("spark.jars", "jars/spark-cassandra-connector_2.12-3.5.1.jar,""jars/spark-sql-kafka-0-10_2.12-3.5.1.jar")`
  - OR keep the config and copy the correct version jars into `.venv/lib/site-packages/pyspark/jars/` *( hardly work on Windows since not every folder is displayed there)*

- jars file specified for Spark is wrong, `pyspark --version` currently at Spark3.5.1 and Scala2.12

- `spark-master` and `spark-worker` can be seen *inactive* on Docker Desktop but if it is found at `localhost:9090` normally then skip it *(thus meaning it is active (iguess?))*
 - *Also that mean the compose file built correctly*

- Running `spark_stream` to create the keyspace and table *(commenting out lines beyond `insert_data()`)*

- When that worked, these in Cassandra will work:
```
docker exec -it cassandra cqlsh -u cassandra -p cassandra localhost 9042
# then
cassandra@cqlsh> describe spark_streams.created_users;
```

- Next step: `spark-submit --master spark://localhost:7077 spark_stream.py`
- Error connecting to Kafka topic -> Connector problem -> `spark-submit` do not automatically install the required jars

**New information:**
  - This line is to validate the Spark version in the container when needed: `docker exec -it realtime-streaming-spark-master-1 spark-submit --version`
  - Runnning `spark_stream` on WSL, Kafka at 'localhost:9092' wont be recognized *not for on spark-master*

- `spark-submit` cannot handle method `connect_to_kafka()`:
  - tried `networks: confluent: bridge` -> webserver breaks down if without `compose down` -> all are healthy -> spark-submit fails -> tried `host.docker.internal:9092` -> fails
  - trying `host.docker.internal:9092` without network-driver-bridge'
  - trying `spark-submit --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.1,com.datastax.spark:spark-cassandra-connector_2.12:3.5.1 spark_stream.py` -> worked
- when it works, you shall see this:
  - On `spark-submit` terminal:
    ```
    25/08/05 11:31:34 INFO MicroBatchExecution: Streaming query made progress: {
      "id" : "71a723a1-6b75-4964-bf07-7d1dd61e25a1",
      "runId" : "e4a26f69-f5e5-4c41-8a90-1126b53498dc",
      "name" : null,
      "timestamp" : "2025-08-05T04:31:26.408Z",
      "batchId" : 0,
      "numInputRows" : 257,
      "inputRowsPerSecond" : 0.0,
      "processedRowsPerSecond" : 32.98254620123203,
    ```
  - Cassandra side, lines below shall looks good:
    * cqlsh access: `docker exec -it cassandra cqlsh -u cassandra -p cassandra localhost 9042`
    * describe working table: `describe spark_streams.users_created;`
    * checking table: `select * from spark_streams.users_created;`

## Optimizing
- Trying to embbed required connectors, thus minimize this line `spark-submit --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.1,com.datastax.spark:spark-cassandra-connector_2.12:3.5.1 spark_stream.py`
  - Rerun testing on local: `python3 spark_stream.py 1 0`
  - Spark container jars location: `opt/bitnami/spark/jars/`
  - Adding this to compose: `volumes: - ./jars:/opt/bitnami/spark/jars`
  -> Failed external jars declaration is still needed -> Always run in mode `1 1` or `1 0` or just `1`

## Wrapping up development (scratch)
- Specify pipeline architecture
- Write docker-compose
  - Decide the images
  - Decide the ports
  - Decide the networks
  - Decide the volumes
- Write the DAG file
- Test DAG file
- Test Airflow
- Trigger written DAG manually
- Test Control Center
- Write Spark streaming
  - Consume Kafka and feed to Cassandra
  - Decide the flow
  - Decide connectors
    - Integrate the **versions** of connectors with **Spark** and **Scala**
- Test Spark code
- Test Cassandra consumption
- Submit Spark code and test

## Future application
- Streaming pipelines for logs
- ML integration for models: prediction, feature extraction...