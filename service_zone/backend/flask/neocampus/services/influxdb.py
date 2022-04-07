from flask import current_app,jsonify
from influxdb_client import InfluxDBClient, Dialect
import pandas as pd
from datetime import datetime, timedelta
from ..services import influxdb, mongo

import json

def get_handled_data(params):
    #Connection Influxdb
    token = current_app.config['INFLUXDB_TOKEN']
    org = current_app.config['INFLUXDB_ORG']

    # Connection to InfluxDB database
    client = InfluxDBClient(url=current_app.config['INFLUXDB_URL'], token=token, debug=True, verify_ssl=False)

    # Query
    query_api = client.query_api()

    dict_params = {
        'begin_date': datetime.strptime(params['beginDate'], '%Y-%m-%d'), 
        'end_date':  datetime.strptime(params['endDate'], '%Y-%m-%d')
    }

    # InfluxDB Exception 
    # # Adding 1 day to end date when beginDate and endDate are same, else Bad Request is thrown
    if(dict_params.get('begin_date') == dict_params.get('end_date')):
        dict_params['end_date'] = dict_params.get('end_date') + timedelta(days=1)

    """
    Query: using csv library
    1st parameter : query,
    2nd parameter : Dialect instance (object) to specify details / options about CSV result
    3rd parameter : org (for organization)

    All informations above have been copied from InfluxDB UI : Telegraf 
    """
    csv_result = query_api.query_csv(
        f'''from(bucket:"{params['container_name']}")
        |> range(start: begin_date, stop: end_date)''',
        dialect=Dialect(
            header=True, 
            delimiter=",", 
            comment_prefix="#", 
            annotations=[],
            date_time_format="RFC3339"
        ), 
        org=org
    , params=dict_params)

    return csv_result

# To get CSV Result, we put into Pandas DataFrame, which increase filesize
# It's to get exact size in GUI front after putting into Pandas
def create_csv_file(influxdb_result):
    # Put into Panda Dataframe
    df = pd.DataFrame(influxdb_result)

    # Export to CSV 
    csv_bytes = df.to_csv().encode('utf-8')

    # Get nb rows of csv
    index = df.index
    number_of_rows = len(index)

    return csv_bytes, number_of_rows

#Function for connection to influxdb
def connection_inflxdb():
    token = current_app.config['INFLUXDB_TOKEN']
    url = current_app.config['INFLUXDB_URL']
    org = current_app.config['INFLUXDB_ORG']
    client = InfluxDBClient(url=url, token=token, debug=True, verify_ssl=False)
    return client, org

def get_all_measurements(bucket):
    client, org = connection_inflxdb()
    # Query for show all measurements in a bucket
    query = f""" 
    import \"influxdata/influxdb/schema\"

    schema.measurements(bucket: \"{bucket}\")
    """
    # Execute the query
    query_api = client.query_api()
    tables = query_api.query(query=query, org=org)

    # Flatten output tables into list of measurements
    measurements = [row.values["_value"] for table in tables for row in table]

    
    return measurements