export $(cat /.env | xargs)

export ADMIN_DB_PASS=$KEYSTONE_DB_PASSWORD
export ADMIN_PASS=$KEYSTONE_DB_PASSWORD
export OS_USERNAME=admin
export OS_PASSWORD=$KEYSTONE_ADMIN_PASSWORD
export OS_PROJECT_NAME=admin
export OS_USER_DOMAIN_NAME=default
export OS_PROJECT_DOMAIN_NAME=default
# Internal container IP, don't change
export OS_AUTH_URL=http://localhost:5000/v3
export OS_IDENTITY_API_VERSION=3


until curl -s -f -o /dev/null $OS_AUTH_URL
do
  sleep 5
  echo "Waiting for service to be up..."
done

openstack domain create --description "Applications domain" datalake
openstack project create --domain datalake --description "Datalake local users" datalake_user
openstack user create --domain datalake --project datalake_user --password $REST_API_PASSWORD rest_api

openstack role add --domain datalake --user rest_api admin
openstack role add --project datalake_user --user rest_api admin

