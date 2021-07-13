from flask import current_app
from influxdb_client import InfluxDBClient, Dialect
import pandas as pd
from datetime import datetime, timedelta

def get_handled_data(params):
    #Connection Influxdb
    token = "zQZd3Q-5sV0jKKFCXKMoSYd1AqK0HjMX8UFEueLa5lIa76uNch4hsISB0mvL_USZMuhp-rtg9HDOBYv3OpNpuQ=="
    org = "modis"

    # Connection to InfluxDB database
    client = InfluxDBClient(url=current_app.config['INFLUX_URL'], token=token, debug=True)

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
        '''from(bucket:"test2")  
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

    return csv_bytes
