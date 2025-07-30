#!/bin/bash
set -e

if [ -e "/opt/airflow/requirements.txt" ]; then 
    $(command -v pip) install --user -r /opt/airflow/requirements.txt
fi

if [ ! -f "/opt/airflow/airflow.db" ]; then
    airflow db init && \
    airflow user create \
        --username admin \
        --firstname admin \
        --lastname admin \
        --role admin \
        --email admin@example.com \
        --password admin
fi

$(command -v airflow) db upgrade

exec airflow webserver