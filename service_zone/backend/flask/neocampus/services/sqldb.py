from flask import current_app,jsonify
from datetime import datetime, timedelta
import pyodbc
import pandas as pd

import json

#Function for connection to sqldb
def connection_sqldb():
    #Connection sqldb
    SQLSERVER_URL = "Neocampus-datalake-sql.dev.modiscloud.net"
    SQLSERVER_DB = "IndexCPT"
    SQLSERVER_LOGIN = "sa"
    SQLSERVER_PWD = "!ModisSGE"

    driver = "ODBC Driver 17 for SQL Server"

    server = SQLSERVER_URL ##globals()["SQLSERVER_URL"]
    database = SQLSERVER_DB ##globals()["SQLSERVER_DB"]
    username = SQLSERVER_LOGIN ##globals()["SQLSERVER_LOGIN"]
    password = SQLSERVER_PWD ##globals()["SQLSERVER_PWD"]

    # Connection to sqldb database
    ##connection = pyodbc.connect('DRIVER={SQL Server Native Client 11.0};SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+ password)
    connection = pyodbc.connect('DRIVER='+driver+';SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+ password)

    return connection

# To get CSV Result, we put into Pandas DataFrame, which increase filesize
# It's to get exact size in GUI front after putting into Pandas
def create_csv_file(sqldb_result):
    # Put into Panda Dataframe
    df = pd.DataFrame(sqldb_result)

    # Export to CSV 
    csv_bytes = df.to_csv().encode('utf-8')

    # Get nb rows of csv
    index = df.index
    number_of_rows = len(index)

    return csv_bytes, number_of_rows


def get_all_measurements():
    connection = connection_sqldb()
    cursor = connection.cursor()

    # Query
    query_api = "SELECT distinct SUBSTRING(Name, len(Name)-CHARINDEX('.', reverse(Name), CHARINDEX('.', reverse(Name))+1)+2, CHARINDEX('.', reverse(Name), CHARINDEX('.', reverse(Name))+1)) AS Mesurement \
    FROM [IndexCPT].[dbo].[Table_Index] \
    order by 1;"

    cursor.execute(query_api)
    results = cursor.fetchall()

    return results


def get_all_topics(measurement):
    connection = connection_sqldb()
    cursor = connection.cursor()

    # Query
    query_api = "SELECT distinct SUBSTRING(Name, 1, len(Name)-CHARINDEX('.', reverse(Name), CHARINDEX('.', reverse(Name))+1)) As Topic \
    FROM [IndexCPT].[dbo].[Table_Index] \
    WHERE SUBSTRING(Name, len(Name)-CHARINDEX('.', reverse(Name), CHARINDEX('.', reverse(Name))+1)+2, CHARINDEX('.', reverse(Name), CHARINDEX('.', reverse(Name))+1)) = '" + measurement + "'" \
    " order by 1;"

    cursor.execute(query_api)
    results = cursor.fetchall()
   
    return results


def get_all_data(params):
    connection = connection_sqldb()
    cursor = connection.cursor()

    date_format = "%Y-%m-%d"

    dt_begin_date = datetime.fromtimestamp(int(params['begin_date'])) + timedelta(days=1)
    dt_end_date = datetime.fromtimestamp(int(params['end_date'])) + timedelta(days=1)

    dict_params = {
        'begin_date': dt_begin_date.strftime('%Y-%m-%d'), 
        'end_date':  dt_end_date.strftime('%Y-%m-%d')
    }

    # Query
    query_api = "SELECT TS, Value \
    FROM [IndexCPT].[dbo].[Table_Index] \
    WHERE '" + params['topic'] + "." + params['measurement'] + "' = Name \
    AND TS between cast('" + dict_params['begin_date'] + "' As Date) and  cast('" + dict_params['end_date'] + "' As Date);"

    print(query_api)

    cursor.execute(query_api)
    results = cursor.fetchall()

    data = []
    for row in results:
        data.append({
            '_time':  row[0],
            '_value': row[1],
            '_measurement': params['measurement'],
            'topic': params['topic'],
        })
    
    print(data)

    return data

