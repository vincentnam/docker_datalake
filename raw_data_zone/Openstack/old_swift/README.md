# Run swift in docker

set up parameters in config.py

```
cp config.py.sample config.py
```

run

```
docker-compose up -d
```

stop

```
docker-compose down
```

in case no permission of writing

```
sudo chmod -R 777 dev/*
```