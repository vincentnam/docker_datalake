# Launch airflow

    airflow initdb

    # start the web server, default port is 8080
    airflow webserver -p 8080

    # start the scheduler
    airflow scheduler

# Airflow in Docker

Initialize:

```
docker-compose up airflow-init
```

Run:

```
docker-compose up -d
```

Stop:

```
docker-compose down
```

Reference:
> https://airflow.apache.org/docs/apache-airflow/stable/start/docker.html