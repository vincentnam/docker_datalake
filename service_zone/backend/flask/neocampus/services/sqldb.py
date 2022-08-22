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

    server = SQLSERVER_URL ##globals()["SQLSERVER_URL"]
    database = SQLSERVER_DB ##globals()["SQLSERVER_DB"]
    username = SQLSERVER_LOGIN ##globals()["SQLSERVER_LOGIN"]
    password = SQLSERVER_PWD ##globals()["SQLSERVER_PWD"]

    # Connection to sqldb database
    ##connection = pyodbc.connect('DRIVER={SQL Server Native Client 11.0};SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+ password)
    connection = pyodbc.connect('DRIVER={FreeTDS};SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+ password)

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
    results = cursor.fetchone()

    # Flatten output tables into list of measurements
    measurements = [row[0] for table in results for row in table]
    
    return measurements

def get_all_topics(params):
    connection = connection_sqldb()
    cursor = connection.cursor()

    # Query
    query_api = "SELECT distinct SUBSTRING(Name, 1, len(Name)-CHARINDEX('.', reverse(Name), CHARINDEX('.', reverse(Name))+1)) As Topic \
    FROM [IndexCPT].[dbo].[Table_Index] \
    WHERE SUBSTRING(Name, len(Name)-CHARINDEX('.', reverse(Name), CHARINDEX('.', reverse(Name))+1)+2, CHARINDEX('.', reverse(Name), CHARINDEX('.', reverse(Name))+1)) = " + params['measurement'] + \
    " order by 1;"

    cursor.execute(query_api)
    results = cursor.fetchone()

    # Flatten output tables into list of measurements
    topics = [row[0] for table in results for row in table]
    
    return topics

def get_all_data(params):
    connection = connection_sqldb()
    cursor = connection.cursor()

    dict_params = {
        'begin_date': datetime.strptime(params['beginDate'], '%Y-%m-%d'), 
        'end_date':  datetime.strptime(params['endDate'], '%Y-%m-%d')
    }

    #dict_params.get('begin_date')
    #dict_params.get('end_date')

    # Query
    query_api = "SELECT Value \
    FROM [IndexCPT].[dbo].[Table_Index] \
    WHERE len(Name) - len(replace(Name,'.','')) >=2 \
    AND " + params['measurement'] + " = SUBSTRING(Name, len(Name)-CHARINDEX('.', reverse(Name), CHARINDEX('.', reverse(Name))+1)+2, CHARINDEX('.', reverse(Name), CHARINDEX('.', reverse(Name))+1)) \
    AND " + params['topic']+ " = SUBSTRING(Name, 1, len(Name)-CHARINDEX('.', reverse(Name), CHARINDEX('.', reverse(Name))+1)) \
    AND TS between cast(" + params['beginDate'] + " As Date) and  cast(" + params['endDate'] + " As Date);"

    cursor.execute(query_api)
    row = cursor.fetchone()

    results = cursor.fetchone()

    # Flatten output tables into list of measurements
    results_data = [row[0] for table in results for row in table]
    
    return results_data

