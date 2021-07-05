# Web Service

### Config

Create the config file and set the variables for the current environment

```
cp flask/neocampus/config.py.sample flask/neocampus/config.py
```

### Run

- production
    ```shell
    docker-compose up -d
    ```
- development
    ```shell
    docker-compose -f docker-compose-dev.yml up -d
    ```

### Stop

```shell
docker-compose down
```

### Monitor log

```shell
docker-compose logs -f
```
