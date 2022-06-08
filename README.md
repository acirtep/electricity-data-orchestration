# electricity-data-orchestration
Orchestration of RPA and ELT for home electricity overview


# Setup

1. git pull on Synology NAS
1. `cp env_vars_example.env > env_vars.env` and set the correct values
1. Run `docker-compose up airflow-init` to setup the db for airflow
1. Run `docker-compose up` to run airflow services
1. Airflow is hosted on localhost:8085 