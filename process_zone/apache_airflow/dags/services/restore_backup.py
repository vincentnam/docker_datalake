import sys
import os
from datetime import strftime
import pyodbc
from time import gmtime, sleep
import tempfile
import config

def restore_backup(data, filename):
    driver = "ODBC Driver 19 for SQL Server"
    
    localserver = config.mssqlserver_url
    db_environment = config.mssqlserver_db_environment
    localusername = config.mssqlserver_user
    password = config.mssqlserver_pwd
    
    fp = tempfile.NamedTemporaryFile()
    fp.write(data)
    fp.seek(0)
    name_file_temp = fp.name
        
    connectionString = (('DRIVER='+driver+';PORT=1433;SERVER='+localserver +
                    ';PORT=1443;DATABASE=' + db_environment + ';UID='+localusername+';PWD=' + password))
    db_connection = pyodbc.connect(connectionString, autocommit=True)
    cursor = db_connection.cursor()
    
    if filename == "IndexCPT":
        restoreddatabase = "IndexCPT"
        sql = """  
        USE [master]
        RESTORE DATABASE ["""+restoreddatabase+"""] FROM  
        DISK = '"""+name_file_temp+"""' 
        WITH MOVE 'GTE_UPS_SQL_INDEX_CPT' to '/var/opt/mssql/data/GTE_UPS_SQL_INDEX_CPT.mdf'
        , MOVE 'GTE_UPS_SQL_INDEX_CPT_log' to '/var/opt/mssql/data/GTE_UPS_SQL_INDEX_CPT_log.ldf'
        , NORECOVERY
        """
        
    if filename == "TRENDTABLE":
        restoreddatabase = "TRENDTABLE"
        sql = """  
        USE [master]
        RESTORE DATABASE ["""+restoreddatabase+"""] FROM  
        DISK = '"""+name_file_temp+"""' 
        WITH MOVE 'GTE_UPS_SQLSERVEREVAL' to '/var/opt/mssql/data/GTE_UPS_SQLSERVEREVAL.mdf' 
        , MOVE 'GTE_UPS_SQLSERVEREVAL_log' to '/var/opt/mssql/data/GTE_UPS_SQLSERVEREVAL_log.ldf'
        , NORECOVERY
        """
        
    if filename == "BigData":
        restoreddatabase = "BigData"
        sql = """  
        USE [master]
        RESTORE DATABASE ["""+restoreddatabase+"""] FROM  
        DISK = '"""+name_file_temp+"""' 
        WITH MOVE 'BigData' to '/var/opt/mssql/data/BigData.mdf'
        , MOVE 'BigData_log' to '/var/opt/mssql/data/BigData.ldf'
        , NORECOVERY
        """
    
    cursor.execute(sql)
    db_connection1 = pyodbc.connect(connectionString)
    cursor1 = db_connection1.cursor()
    database_restored_sql = """select top 1 * from msdb.dbo.restorehistory order by restore_date desc"""
    cursor1.execute(database_restored_sql)
    dataset = cursor1.fetchall()
    tquery = """        
    SELECT session_id as SPID, command, a.text AS Query, start_time, percent_complete, dateadd(second,estimated_completion_time/1000, getdate()) as estimated_completion_time FROM sys.dm_exec_requests r CROSS APPLY sys.dm_exec_sql_text(r.sql_handle) a WHERE r.command in ('BACKUP DATABASE','RESTORE DATABASE')       
    """
    print('Percentage Restored: ', end='', flush=True)
    while restoreddatabase != dataset[0][2]:
        sleep(5)
        cursor1.execute(database_restored_sql)
        dataset = cursor1.fetchall()
        cursor1.execute(tquery)
        tdataset = cursor1.fetchall()
        if len(tdataset) > 0:
            if tdataset[0][4] > 99.99:
                print(str(tdataset[0][4])[0:3] + '%', end=' ', flush=True)
            else:
                print(str(tdataset[0][4])[0:2] + '% ', end=' ', flush=True)
    db_connection.autocommit = False
    
    return "Done"

sys.modules[__name__] = restore_backup