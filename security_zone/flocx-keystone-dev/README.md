## Configuration

Configure passwords in a [.env][] file like this:

[.env]: https://docs.docker.com/compose/environment-variables/#the-env-file

```
KEYSTONE_ADMIN_PASSWORD=secret.ks.admin.password
KEYSTONE_DB_PASSWORD=secret.db.user.password
MYSQL_ROOT_PASSWORD=secret.db.root.password
```

## Running it

To start up mysql and keystone:

```
docker-compose up -d
```

This will expose keystone on `localhost` port `5000`. You can grab a `clouds.yaml` file from the container for use with the `openstack` client:

```
docker-compose exec keystone cat /root/clouds.yaml > clouds.yaml
```

Once you have this in your current directory, set the `OS_CLOUD` environment variable:

```
export OS_CLOUD=openstack-public
```

And then you can run OpenStack commands:

```
openstack catalog list
```

## Creating users and projects

If you have [ansible][] available (`sudo yum install ansible`), you can use the included `create-users-projects.yml` playbook to create a set of projects and users:

```
ansible-playbook create-users-projects.yml
```

[ansible]: https://www.ansible.com/
