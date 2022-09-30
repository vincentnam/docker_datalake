#!/bin/sh

mysql -u root -p${MYSQL_ROOT_PASSWORD} mysql <<EOF
CREATE DATABASE IF NOT EXISTS flocx_market;
GRANT ALL PRIVILEGES ON flocx_market.* TO 'flocx_market'@'localhost'
	IDENTIFIED BY '${MARKET_DB_PASSWORD}';
GRANT ALL PRIVILEGES ON flocx_market.* TO 'flocx_market'@'%'
	IDENTIFIED BY '${MARKET_DB_PASSWORD}';

CREATE DATABASE IF NOT EXISTS flocx_provider;
GRANT ALL PRIVILEGES ON flocx_provider.* TO 'flocx_provider'@'localhost'
	IDENTIFIED BY '${PROVIDER_DB_PASSWORD}';
GRANT ALL PRIVILEGES ON flocx_provider.* TO 'flocx_provider'@'%'
	IDENTIFIED BY '${PROVIDER_DB_PASSWORD}';
EOF
