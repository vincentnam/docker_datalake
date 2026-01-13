#!/bin/bash
docker compose down --volumes --remove-orphans


rm .env 
rm -rf ./dags ./logs ./plugins ./config
