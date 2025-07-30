27/07 20:00
- create .venv
- install apache-airflow
- create the kafka_stream
- airflow only support Linux, so the env must be compatible to Linux
- recreate .venv
- trying auto activate env on creating terminal
- too messy, just use every time 
`
    source .venv/bin/activate
`
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
