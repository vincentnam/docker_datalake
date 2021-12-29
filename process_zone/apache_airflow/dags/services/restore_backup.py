import sys
import pyodbc
from time import gmtime, sleep
import tempfile
import config
import paramiko
from scp import SCPClient

def restore_backup(data, filename):
    #Create a temp file for the backup
    fp = tempfile.NamedTemporaryFile()
    fp.write(data)
    fp.seek(0)
    name_file_temp = fp.name
    
    # Create connection to ms sql server
    driver = "ODBC Driver 17 for SQL Server"
    
    localserver = config.mssqlserver_url
    localusername = config.mssqlserver_user
    password = config.mssqlserver_pwd
    
    connectionString = (('DRIVER={'+driver+'};SERVER='+localserver +
                        ';UID='+localusername+';PWD=' + password))
    db_connection = pyodbc.connect(connectionString, autocommit=True)
    cursor = db_connection.cursor()
    
    #Mouv tempfile in docker ms sql server on sqlserver machine
    host = config.host_server_ms_sql
    user = config.host_server_ms_sql_user
    password_sevice_scp = config.host_server_ms_sql_password
    path_distant = config.path_server_ms_sql_file
    
    #Recupération du nom du fichier temp
    name_file_temp_split = name_file_temp.split('/')
    name_file_temp_after_split = name_file_temp_split[len(name_file_temp_split) -1]

    #Connection SSH to machine SQL Server
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.load_system_host_keys()
    ssh.connect(hostname=host, 
                username=user,
                password=password_sevice_scp)
    
    # SCPCLient takes a paramiko transport as its only argument
    scp = SCPClient(ssh.get_transport())

    #Mouv file airflow to machine SQL Server
    scp.put(name_file_temp, name_file_temp_after_split)

    #Copy file to docker container
    container_id = config.id_container_ms_sql
    command = "sudo docker cp " + name_file_temp_after_split + " " + container_id +":/var/opt/sqlserver/backup/"+ name_file_temp_after_split
    ssh.exec_command(command)

    sleep(60)

    path = path_distant+name_file_temp_after_split
    #Change chmod file to 777
    command_chmod = "sudo chmod 777 -R /opt/docker_datalake/raw_data_zone/ms_sql_server/sqlserver/backup/"+ name_file_temp_after_split
    ssh.exec_command(command_chmod)

    sleep(30)
    
    #Config request restore in function of name of file upload
    if filename == "IndexCPT":
        restoreddatabase = "IndexCPT"
        sql = """
        RESTORE DATABASE ["""+restoreddatabase+"""] FROM  
        DISK = '/var/opt/sqlserver/backup/"""+name_file_temp_after_split+"""' 
        WITH MOVE 'GTE_UPS_SQL_INDEX_CPT' to '/var/opt/mssql/data/GTE_UPS_SQL_INDEX_CPT.mdf'
        , MOVE 'GTE_UPS_SQL_INDEX_CPT_log' to '/var/opt/mssql/data/GTE_UPS_SQL_INDEX_CPT_log.ldf'
        , NORECOVERY
        , REPLACE
        """
        
    if filename == "TRENDTABLE":
        restoreddatabase = "TRENDTABLE"
        sql = """
        RESTORE DATABASE ["""+restoreddatabase+"""] FROM  
        DISK = '/var/opt/sqlserver/backup/"""+name_file_temp_after_split+"""' 
        WITH MOVE 'GTE_UPS_SQLSERVEREVAL' to '/var/opt/mssql/data/GTE_UPS_SQLSERVEREVAL.mdf' 
        , MOVE 'GTE_UPS_SQLSERVEREVAL_log' to '/var/opt/mssql/data/GTE_UPS_SQLSERVEREVAL_log.ldf'
        , NORECOVERY
        , REPLACE
        """
        
    if filename == "BigData":
        restoreddatabase = "BigData"
        sql = """
        RESTORE DATABASE ["""+restoreddatabase+"""] FROM  
        DISK = '/var/opt/sqlserver/backup/"""+name_file_temp_after_split+"""' 
        WITH MOVE 'BigData' to '/var/opt/mssql/data/BigData.mdf'
        , MOVE 'BigData_log' to '/var/opt/mssql/data/BigData.ldf'
        , NORECOVERY
        , REPLACE
        """
    
    cursor.execute(sql)
    #Delete temp file of machine SQL Server and docker container
    command_rm_mssql_tempsfile = "sudo rm /opt/docker_datalake/raw_data_zone/ms_sql_server/sqlserver/backup/"+ name_file_temp_after_split
    command_rm_home_tempsfile = "sudo rm "+ name_file_temp_after_split
    ssh.exec_command(command_rm_mssql_tempsfile)
    ssh.exec_command(command_rm_home_tempsfile)
    scp.close()
    return "Done"

sys.modules[__name__] = restore_backup