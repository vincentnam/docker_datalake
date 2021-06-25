import pandas as pd
import sys
from datetime import timedelta, datetime, date
import datetime
from textwrap import dedent
from io import StringIO
from influxdb_client import InfluxDBClient
from influxdb_client.client.write_api import SYNCHRONOUS
from pymongo import MongoClient
import history_data
import get_positions
import config

# Fonction de traitement d'un fichier CSV Time Series
def extract_transform_load_time_series_csv(swift_result, swift_container, swift_id, process_type):
    result = []
    # List fields timestamp
    timestamp_fields_list = [
        "timestamp",
        "temps",
        "date",
        "measuretime"
    ]
    # List fields value
    value_fields_list = [
        "value",
        "valeur",
        "reading",
        "payload.value"
    ]
    # Data proccessing swift_result of bytes to dataframe
    s=str(swift_result,'utf-8').replace("\\n", "\n")
    data = StringIO()
    data.write(s)
    data.seek(0)
    df = pd.read_csv(data, sep=",")
    columns = df.columns
    
    #Recherche des positions des valeurs 
    position_timestamp, position_value, position_topic, position_payload_value_units = get_positions(
        columns, 
        timestamp_fields_list, 
        value_fields_list
    )
    
    # Récupération du token, organisation, bucket et url pour Influxdb
    token = config.token_influxdb
    org = config.org_influxdb
    bucket = config.bucket_influxdb
    url = config.url_influxdb

    #Connection Influxdb
    client = InfluxDBClient(url=url, token=token, debug=True)
    write_api = client.write_api(write_options=SYNCHRONOUS)
    
    for index, line in df.iterrows():
        # Parsing date timestamp to date milliseconds
        date = line[position_timestamp].replace('t', " ")
        date = date.replace('z', "")
        date = date.replace('.000', "")
        date = date.replace('-', "/")
        datetime_object = datetime.datetime.strptime(date, '%Y/%m/%d %H:%M:%S')
        date_milliseconds = int(round(datetime_object.timestamp() * 1000000000))
        history_data(process_type, swift_container, swift_id, "parsing_date_timestamp_to_date_milliseconds", line[position_timestamp], date_milliseconds)
        new_data = []
        values = {}
        tags = {}
        # Parsing and config values
        if "energy" not in line[position_topic]:
            #Remplace le (.) par (_) car influxdb n'accepte pas les points dans les string
            unit = line[position_payload_value_units].replace(".", "_")
            values["value"] = float(line[position_value])
            old_tags = tags
            # Parsing and config tags
            for key, value in enumerate(columns):
                if position_payload_value_units != value and position_value != value:
                    val = value.replace(".", "_")
                    if line[value] == "":
                        tags[val] = ""
                    else:
                        tags[val] = str(line[value])
            history_data(process_type, swift_container, swift_id, "config_tags", old_tags, tags)
            # Create variable for upload in influxdb
            new_data.append(
                {
                    "measurement": unit,
                    "tags": tags,
                    "fields": values,
                    "time": date_milliseconds
                }
            )
            result.append(new_data)
            line = {"line": line}
            # Upload in influxdb
            write_api.write(bucket, org, new_data, protocol='json') 
        else:
            # Création d'un tuple pour pourvoir relier les values avec leur unit_values
            list_of_tuples = list(zip(line[position_payload_value_units].strip('][').split(','), line[position_value].strip('][').split(',')))
            for l in list_of_tuples:
                dt = []
                unit, v = l
                #Remplacer . par _ car influxdb not . in string
                unit = unit.replace(".", "_")
                unit = unit.replace('"', '')
                values["value"] = float(v)
                old_tags = tags
                # Parsing and config tags
                for key, value in enumerate(columns):
                    if position_payload_value_units != value and position_value != value:
                        #Remplacer . par _ car influxdb not . in string
                        val = value.replace(".", "_")
                        if line[value] == "":
                            tags[val] = ""
                        else:
                            tags[val] = str(line[value])
                history_data(process_type, swift_container, swift_id, "config_tags", old_tags, tags)
                # Create variable for upload in influxdb
                dt.append(
                    {
                        "measurement": unit,
                        "tags": tags,
                        "fields": values,
                        "time": date_milliseconds
                    }
                )
                result.append(dt)
                # Upload in influxdb
                write_api.write(bucket, org, dt, protocol='json') 
    return result


sys.modules[__name__] = extract_transform_load_time_series_csv

