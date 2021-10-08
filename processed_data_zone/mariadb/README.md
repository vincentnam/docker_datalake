# Run MariaDB in docker

## Configuration

Set up mariaDB user and password in `.env`

```
cp .env.sample .env
```

```
MARIADB_ROOT_PASSWORD=  
MARIADB_DATABASE=  
MARIADB_USER=  
MARIADB_PASSWORD=
```

## Run

```
./run.sh
```

## Stop

```
./stop.sh
```

## Set up service in linux

```
sudo vim /etc/systemd/system/docker.mariadb.service
```

```
[Unit]
Description=MariaDB Service
After=docker.service
Requires=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/opt/docker_datalake/processed_data_zone/mariadb
ExecStart=bash run.sh
ExecStop=bash stop.sh

[Install]
WantedBy=default.target
```

## Enable the service

```
systemctl enable docker.mariadb.service
```

## Run and stop as system service

```
systemctl start docker.mariadb.service
```

```
systemctl stop docker.mariadb.service
```
