#set -x
CERT_INFO="/C=FR/ST=Toulouse/L=Toulouse/O=Global Security/OU=IT Department/CN=datalake"

docker-compose down
## Clean up env
rm -rf ./cache
rm -rf ./volumes
rm -rf ./certificates
#rm -rf ./volumes
rm -rf ./data
rm .env



#docker system prune -f -a
#docker volume prune -f


## Config files

# .env file for docker-compose
cat >> .env <<EOF
COMPOSE_PROJECT_NAME=datalake
MYSQL_ROOT_PASSWORD=root_pwd
MARKET_DB_PASSWORD=database_pwd
PROVIDER_DB_PASSWORD=provider_pwd
KEYSTONE_DB_USER=keystone
KEYSTONE_DB_PASSWORD=keystone_pwd
KEYSTONE_DB_NAME=keystone
KEYSTONE_ADMIN_PASSWORD=admin_pass
REST_API_PASSWORD=test
MONGO_URL="192.167.3.100:27017"
MONGO_ADMIN="admin_metadata_management"
MONGO_PWD="password_admin_mongo"
MONGO_DB_AUTH="admin"

EOF

export $(cat .env | xargs)

## Generate SSL certificate

mkdir certificates

#mkdir certificates/deployment_keys

echo "##### Security zone - Keystone"
##### Security zone - Keystone

## Create temporary files

WORKING_DIR_PATH="./cache/security_zone/"
APP_DEPLOYMENT_DIR="flocx-keystone-dev"
ROOT_PATH="../../"
APP_NAME="Openstack_Keystone"

mkdir certificates/$APP_NAME
openssl req -nodes -newkey rsa:2048 -keyout certificates/$APP_NAME/$APP_NAME.key -out certificates/$APP_NAME/$APP_NAME.csr -subj "$CERT_INFO"
openssl x509 -req -sha256 -days 365 -in certificates/$APP_NAME/$APP_NAME.csr -signkey certificates/$APP_NAME/$APP_NAME.key -out certificates/$APP_NAME/$APP_NAME.pem


mkdir -p $WORKING_DIR_PATH
cp -r ${ROOT_PATH}security_zone/$APP_DEPLOYMENT_DIR/ $WORKING_DIR_PATH
cp $WORKING_DIR_PATH/$APP_DEPLOYMENT_DIR/.env.sample $WORKING_DIR_PATH/$APP_DEPLOYMENT_DIR/.env

#mkdir certificates/$APP_DEPLOYMENT_DIR
#openssl req -nodes -newkey rsa:2048 -keyout certificates/$APP_DEPLOYMENT_DIR/$APP_DEPLOYMENT_DIR.key -out certificates/$APP_DEPLOYMENT_DIR/$APP_DEPLOYMENT_DIR.csr -subj "$CERT_INFO"
#openssl x509 -req -sha256 -days 365 -in certificates/$APP_DEPLOYMENT_DIR/$APP_DEPLOYMENT_DIR.csr -signkey certificates/$APP_DEPLOYMENT_DIR/$APP_DEPLOYMENT_DIR.key -out certificates/$APP_DEPLOYMENT_DIR/$APP_DEPLOYMENT_DIR.pem
#mkdir $WORKING_DIR_PATH/$APP_DEPLOYMENT_DIR/certificates/keystone
mkdir $WORKING_DIR_PATH/$APP_DEPLOYMENT_DIR/certificates/
cp certificates/$APP_DEPLOYMENT_DIR/$APP_DEPLOYMENT_DIR.pem $WORKING_DIR_PATH/$APP_DEPLOYMENT_DIR/certificates/signing_cert.pem
cp certificates/$APP_DEPLOYMENT_DIR/$APP_DEPLOYMENT_DIR.key $WORKING_DIR_PATH/$APP_DEPLOYMENT_DIR/certificates/signing_key.key

# Openstack Keystone config file

cat > $WORKING_DIR_PATH/$APP_DEPLOYMENT_DIR/runtime/keystone.j2.conf <<EOF
[DEFAULT]
debug = {{ environ.KEYSTONE_DEBUG|default('false') }}
log_file =


[database]
{% set keystone_db_user = environ.KEYSTONE_DB_USER|default('keystone') %}
{% set keystone_db_host = environ.KEYSTONE_DB_HOST|default('localhost') %}
{% set keystone_db_port = environ.KEYSTONE_DB_PORT|default('3306') %}
{% set keystone_db_name = environ.KEYSTONE_DB_NAME|default('keystone') %}
{% set keystone_db_pass = environ.KEYSTONE_DB_PASSWORD|default('insert-password-here') %}
connection = mysql+pymysql://{{ keystone_db_user }}:{{ keystone_db_pass }}@{{ keystone_db_host }}:{{ keystone_db_port }}/{{ keystone_db_name }}

[token]
provider = fernet
expiration=14400


[ldap]
url = ldap://192.167.0.100
suffix = dc=datalakelocal,dc=com
user = cn=admin,dc=datalakelocal,dc=com
password = admin_pass
query_scope = sub
user_tree_dn = dc=datalakelocal,dc=com
user_filter = (|(cn=admin)(objectClass=inetOrgPerson))
group_tree_dn = ou=groups,dc=datalakelocal,dc=com
user_allow_create = False
user_allow_update = False
user_allow_delete = False
group_allow_create = False
group_allow_update = False
group_allow_delete = False
user_id_attribute      = uidNumber
user_name_attribute    = cn
user_mail_attribute    = mail
user_pass_attribute    = userPassword
user_enabled_attribute = userAccountControl
user_enabled_mask      = 2
user_enabled_invert    = false
user_enabled_default   = 512
group_id_attribute = cn
group_name_attribute = ou
group_member_attribute = member
group_desc_attribute = description
user_enabled_attribute = userAccountControl

[identity]
#driver = ldap
driver = sql
[assignment]
driver = sql

[oslo_policy]
enforce_scope =False
EOF

echo ""
echo "###################################### Security zone - OpenLDAP ######################################"
echo "TODO : INITIALISATION SCRIPT WITH USER, OBJECTS AND ORGANIZATION CREATION"
echo ""
#### Security zone - OpenLDAP

WORKING_DIR_PATH="./cache/security_zone/"
APP_NAME="OpenLDAP"

ROOT_PATH="../../"


mkdir certificates/$APP_NAME
openssl req -nodes -newkey rsa:2048 -keyout certificates/$APP_NAME/$APP_NAME.key -out certificates/$APP_NAME/$APP_NAME.csr -subj "$CERT_INFO"
openssl x509 -req -sha256 -days 365 -in certificates/$APP_NAME/$APP_NAME.csr -signkey certificates/$APP_NAME/$APP_NAME.key -out certificates/$APP_NAME/$APP_NAME.pem

###### Raw data zone - Openstack Swift
echo ""
echo "###################################### Raw data zone - Openstack Swift ######################################"
echo ""
echo ""


WORKING_DIR_PATH="./cache/raw_data_zone/"
APP_DEPLOYMENT_DIR="Openstack"
ROOT_PATH="../../"
APP_NAME="Openstack_Swift"


mkdir -p $WORKING_DIR_PATH
cp -r ${ROOT_PATH}raw_data_zone/$APP_DEPLOYMENT_DIR/ $WORKING_DIR_PATH
#cp $WORKING_DIR_PATH/$APP_DEPLOYMENT_DIR/config.py.sample $WORKING_DIR_PATH/$APP_DEPLOYMENT_DIR/config.py
mkdir $WORKING_DIR_PATH/$APP_DEPLOYMENT_DIR/swift/certificates

## SSL Certificate generation
mkdir certificates/$APP_NAME
openssl req -nodes -newkey rsa:2048 -keyout certificates/$APP_NAME/$APP_NAME.key -out certificates/$APP_NAME/$APP_NAME.csr -subj "$CERT_INFO"
openssl x509 -req -sha256 -days 365 -in certificates/$APP_NAME/$APP_NAME.csr -signkey certificates/$APP_NAME/$APP_NAME.key -out certificates/$APP_NAME/$APP_NAME.pem

cp certificates/$APP_NAME/$APP_NAME.pem $WORKING_DIR_PATH/$APP_DEPLOYMENT_DIR/swift/certificates/signing_cert.pem
cp certificates/$APP_NAME/$APP_NAME.key $WORKING_DIR_PATH/$APP_DEPLOYMENT_DIR/swift/certificates/signing_key.key

#cp certificates/signing_cert.pem certificates/signing_key.pem $WORKING_DIR_PATH/$APP_DEPLOYMENT_DIR/swift/certificates/

## Config

echo 'AIRFLOW_API_URL = "'"$AIRFLOW_URL"'"'> $WORKING_DIR_PATH/$APP_DEPLOYMENT_DIR/swift/config.py

###### Metadata data zone
echo ""
echo "###################################### Metadata zone - MongoDB #########################################################"
echo ""
echo ""
WORKING_DIR_PATH="./cache/metadata_management_zone/"
APP_DEPLOYMENT_DIR="mongodb"
ROOT_PATH="../../"
APP_NAME="MongoDB"


mkdir -p $WORKING_DIR_PATH
cp -r ${ROOT_PATH}metadata_management_zone/$APP_DEPLOYMENT_DIR/ $WORKING_DIR_PATH
#cp $WORKING_DIR_PATH/$APP_DEPLOYMENT_DIR/.env.sample $WORKING_DIR_PATH/$APP_DEPLOYME#cp certificates/signing_cert.pem certificates/signing_key.pem $WORKING_DIR_PATH/$APP_DEPLOYMENT_DIR/swift/certificates/
NT_DIR/.env

## SSL Certificate generation
mkdir certificates/$APP_NAME
mkdir $WORKING_DIR_PATH/$APP_DEPLOYMENT_DIR/certificates
openssl req -nodes -newkey rsa:2048 -keyout certificates/$APP_NAME/$APP_NAME.key -out certificates/$APP_NAME/$APP_NAME.csr -subj "$CERT_INFO"
openssl x509 -req -sha256 -days 365 -in certificates/$APP_NAME/$APP_NAME.csr -signkey certificates/$APP_NAME/$APP_NAME.key -out certificates/$APP_NAME/$APP_NAME.pem

cp certificates/$APP_NAME/$APP_NAME.pem $WORKING_DIR_PATH/$APP_DEPLOYMENT_DIR/certificates/signing_cert.pem
cat certificates/$APP_NAME/$APP_NAME.key >> $WORKING_DIR_PATH/$APP_DEPLOYMENT_DIR/certificates/signing_cert.pem



###### Process zone - Apache Airflow
echo ""
echo "###################################### Process zone - Apache Airflow #########################################################"
echo ""
echo ""
WORKING_DIR_PATH="./cache/process_zone/"
APP_DEPLOYMENT_DIR="apache_airflow"
ROOT_PATH="../../"

_PIP_ADDITIONAL_REQUIREMENTS='apache-airflow-providers-mongo pymongo python-swiftclient influxdb-client scp'

CONTENT_DOCKERFILE="FROM apache/airflow:2.5.1\nRUN pip install ${_PIP_ADDITIONAL_REQUIREMENTS}\nENV PYTHONPATH "${PYTHONPATH}:.""

mkdir -p $WORKING_DIR_PATH
cp -r ${ROOT_PATH}process_zone/$APP_DEPLOYMENT_DIR/ $WORKING_DIR_PATH

export AIRFLOW_PROJ_DIR=$(pwd)/cache/process_zone/apache_airflow

echo "AIRFLOW_UID=$(id -u)" >> .env

cp $AIRFLOW_PROJ_DIR/dags/config.py.sample $AIRFLOW_PROJ_DIR/dags/config.py
sed -i 's/schedule_interval = ""/schedule_interval = "@daily"/g' $AIRFLOW_PROJ_DIR/dags/config.py
cp $AIRFLOW_PROJ_DIR/dags/config.py $AIRFLOW_PROJ_DIR/dags/old_dags/config.py
cp $AIRFLOW_PROJ_DIR/dags/config.yml $AIRFLOW_PROJ_DIR/dags/old_dags/config.yml


echo $CONTENT_DOCKERFILE > ./cache/process_zone/apache_airflow/Dockerfile

#### Process zone - Apache Spark
echo ""
echo "###################################### Process zone - Apache Spark #########################################################"
echo ""
echo ""

WORKING_DIR_PATH="./cache/process_zone/"
APP_DEPLOYMENT_DIR="apache_spark"
ROOT_PATH="../../"
APP_NAME="Apache_Spark"


## SSL Certificate generation

mkdir certificates/$APP_NAME
mkdir $WORKING_DIR_PATH$APP_DEPLOYMENT_DIR/certificates
openssl req -nodes -newkey rsa:2048 -keyout certificates/$APP_NAME/$APP_NAME.key -out certificates/$APP_NAME/$APP_NAME.csr -subj "$CERT_INFO"
openssl x509 -req -sha256 -days 365 -in certificates/$APP_NAME/$APP_NAME.csr -signkey certificates/$APP_NAME/$APP_NAME.key -out certificates/$APP_NAME/$APP_NAME.pem



cp -r ${ROOT_PATH}process_zone/$APP_DEPLOYMENT_DIR/ $WORKING_DIR_PATH
mkdir $WORKING_DIR_PATH$APP_DEPLOYMENT_DIR/certificates
cp certificates/$APP_NAME/$APP_NAME.pem $WORKING_DIR_PATH/$APP_DEPLOYMENT_DIR/certificates
cp certificates/$APP_NAME/$APP_NAME.key $WORKING_DIR_PATH/$APP_DEPLOYMENT_DIR/certificates
cp certificates/MongoDB/MongoDB.pem $WORKING_DIR_PATH/$APP_DEPLOYMENT_DIR/certificates
cp certificates/Openstack_Swift/Openstack_Swift.pem $WORKING_DIR_PATH/$APP_DEPLOYMENT_DIR/certificates

rm $WORKING_DIR_PATH/$APP_APP_DEPLOYMENT_DIR/apache_spark/Dockerfile
cat >> $WORKING_DIR_PATH/$APP_APP_DEPLOYMENT_DIR/apache_spark/Dockerfile << EOF

FROM openjdk:11

ENV SBT_VERSION 1.6.2

RUN curl -L -o sbt-\$SBT_VERSION.zip https://github.com/sbt/sbt/releases/download/v\$SBT_VERSION/sbt-\$SBT_VERSION.zip
RUN unzip sbt-\$SBT_VERSION.zip -d ops

USER root
WORKDIR project

ADD . /project

RUN /ops/sbt/bin/sbt compile
CMD /ops/sbt/bin/sbt run
EOF


#### Service zone - Backend
echo ""
echo "###################################### Service zone - Backend #########################################################"
echo ""
echo ""
WORKING_DIR_PATH="./cache/service_zone/"
APP_DEPLOYMENT_DIR="backend"
ROOT_PATH="../../"

mkdir -p $WORKING_DIR_PATH
cp -r ${ROOT_PATH}service_zone/$APP_DEPLOYMENT_DIR/ $WORKING_DIR_PATH

rm ${WORKING_DIR_PATH}backend/flask/neocampus/config.py

cat >> ${WORKING_DIR_PATH}backend/flask/neocampus/config.py << EOF

MONGO_URL = "192.167.3.100:27017"
MONGO_ADMIN = "$MONGO_ADMIN"
MONGO_PWD = "$MONGO_PWD"
MONGO_DB_AUTH = "$MONGO_DB_AUTH"
SWIFT_AUTHURL = "https://192.167.4.100:8080/auth/v1.0"
SWIFT_USER = 'test:tester'
SWIFT_KEY = 'testing'
SWIFT_FILES_DIRECTORY = "/tmp/"
INFLUXDB_URL = "https://url_influxdb:8086"
INFLUXDB_TOKEN = "token_influxdb"
INFLUXDB_ORG = "organisation_influxdb"
INFLUXDB_BUCKET = "nom_du_bucket_influxdb"
USER = "user_serveur_sql"
PASSWORD = "password_user_serveur_sql"
KEYSTONE_URL = "http://192.167.2.100:5000/v3"
KEYSTONE_IP = "192.167.2.100"
PROJECT_ID = "datalake_user"
USER_DOMAIN_ID = "datalake"
USER_ADMIN = "rest_api"
USER_ADMIN_PWD = "$REST_API_PASSWORD"
HOST_URL = "http://192.167.6.100"

BIG_FILE_PATH = "chemin depuis la racine vers le dossier cache d’upload des fichiers"
IP_MACHINE_MONGO = "192.167.3.100"
USER_MACHINE_MONGO = "user_serveur_mongo"
PWD_MACHINE_MONGO = "password_user_serveur_mongo"


SQLSERVER_URL = "http://url_sqlserver"
SQLSERVER_DB = "nom_DB_installation_backup_SGE"
SQLSERVER_LOGIN = "user"
SQLSERVER_PWD = "password_user"

UPLOAD_FOLDER = "nom dossier upload images pour similitude avec / à la fin du nom"
IMAGES_SIMILARITY = "nom_dossier_stockage_resultat_similitude"

EOF
### Service zone - Backend - Nginx


rm ${WORKING_DIR_PATH}backend/nginx/default.conf
cat >> ${WORKING_DIR_PATH}backend/nginx/default.conf << EOF
#
#upstream flask {
#    server 192.167.6.100:5000;
#}
#
#
#server {
#    listen 80;
#    server_name dev.modiscloud.net;
#    charset utf-8;
#    client_body_timeout 3600s;
#    uwsgi_read_timeout 3600s;
#
#    location / {
#        include /etc/nginx/uwsgi_params;
#        uwsgi_pass flask;
#        add_header 'Access-Control-Allow-Origin' '*';
#        add_header 'Access-Control-Allow-Headers' 'access-control-allow-origin,X-Requested-With,Content-Type,cache-control';
#        add_header 'Access-Control-Allow-Credentials' 'true';
#        proxy_buffering on;
#        client_body_buffer_size 500M;
#        client_max_body_size 1G;
#        client_body_timeout 3600s;
#        uwsgi_read_timeout 3600s;
#    }
#}
#
#access_log /var/log/nginx/access.log main;
#error_log /var/log/nginx/error.log warn;
#
#server_tokens off;
#server {
#    listen 80;
#
#    location / {
#        proxy_pass flask;
#    }
#
#}

upstream flask {
  server 192.167.6.100:5000;
}

server {
    listen       80;
    listen  [::]:80;
    server_name  localhost;

    location / {
            include /etc/nginx/uwsgi_params;
            uwsgi_pass flask;
            proxy_buffering on;
            client_body_buffer_size 500M;
            client_max_body_size 1G;
            client_body_timeout 3600s;
            uwsgi_read_timeout 3600s;
    }

    error_page   500 502 503 504  /50x.html;
    location = /50x.html {
        root   /usr/share/nginx/html;
    }


}


EOF




#### Service zone - Frontend
WORKING_DIR_PATH="./cache/service_zone/"
APP_DEPLOYMENT_DIR="frontend"
ROOT_PATH="../../"

mkdir -p $WORKING_DIR_PATH
cp -r ${ROOT_PATH}service_zone/$APP_DEPLOYMENT_DIR/ $WORKING_DIR_PATH
cp $WORKING_DIR_PATH/$APP_DEPLOYMENT_DIR/datalake-react-front/.env.sample $WORKING_DIR_PATH/$APP_DEPLOYMENT_DIR/datalake-react-front/.env



sed -i 's#REACT_APP_SERVER_NAME="http://"#REACT_APP_SERVER_NAME="http://192.167.6.1:80/api"#g' $WORKING_DIR_PATH/$APP_DEPLOYMENT_DIR/datalake-react-front/.env
###### Local launch of architecture


docker compose up airflow-init

#docker compose --profile init_mongodb up
#docker exec MongoDB_init



#docker compose build --no-cache
docker compose up -d
###### Post launch operation*
docker cp ./initialise_keystone.sh Openstack_keystone:/
docker cp ./.env Openstack_keystone:/
docker exec -it Openstack_keystone sh /initialise_keystone.sh

docker cp ./initialise_mongodb.sh MongoDB:/
docker cp ./.env MongoDB:/
docker exec -it MongoDB sh /initialise_mongodb.sh

#sudo docker exec MongoDB mongosh --eval "db.createUser( { user: '$MONGO_ADMIN',pwd: '$MONGO_PWD',roles: [ 'root' ]} )" "mongodb://localhost:27017/admin"
