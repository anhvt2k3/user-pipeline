27/07 20:00
- create .venv
- install apache-airflow
- create the kafka_stream
- airflow only support Linux
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