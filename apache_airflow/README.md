# Launch airflow
    airflow initdb

    # start the web server, default port is 8080
    airflow webserver -p 8080

    # start the scheduler
    airflow scheduler


# Setting localexecutor 
    # Install the repository RPM:
    sudo yum install -y https://download.postgresql.org/pub/repos/yum/reporpms/EL-7-x86_64/pgdg-redhat-repo-latest.noarch.rpm
    
    # Install PostgreSQL:
    sudo yum install -y postgresql96-server
    
    # Optionally initialize the database and enable automatic start:
    sudo /usr/pgsql-9.6/bin/postgresql96-setup initdb
    sudo systemctl enable postgresql-9.6
    sudo systemctl start postgresql-9.6
    
    sudo su - postgres
    psql
    CREATE USER airflow_user PASSWORD test;
    CREATE DATABASE airflow_db;
    GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA PUBLIC to airflow_user;
    

    sudo vim /var/lib/pgsql/9.6/data/pg_hba.conf
    -> set all to "trust" because it's easier