import pandas as pd
import sys
from datetime import timedelta, datetime, date
import datetime
from textwrap import dedent
from io import StringIO
from influxdb_client import InfluxDBClient
from influxdb_client.client.write_api import SYNCHRONOUS
from pymongo import MongoClient
from services import history_data
from services import get_positions
import config

# Fonction de traitement d'un fichier TEXT Time Series


def extract_transform_load_time_series_text(swift_result, swift_container, swift_id, process_type):
    result = []
    # Data proccessing swift_result of bytes to dataframe
    s = str(swift_result, 'utf-8').replace("\\n", "\n")
    lines = StringIO()
    lines.write(s)
    lines.seek(0)

    data = []
    for line in lines:
        line = line.replace("\n", "")
        data.append(line)

    new_data = []

    for line in data[2:]:
        line = line.replace(",", "T")
        line = line.replace(" ", ",")
        new_data.append(line)
    n_d = data[1].split(',')
    d = []
    for line in n_d:
        values = line.split('_')
        v = '_'.join(values[1:])
        d.append(v)

    d = ','.join(d)

    new_data.insert(0, d)
    columns = new_data[0].split(',')
    values = []
    for line in new_data[1:]:
        line = line.split(',')
        if len(line) != len(columns):
            line.append(-999.99)
        values.append(line)
    # print(values)
    df = pd.DataFrame(values, columns=columns)
    columns = df.columns

    values_tags = data[0].split(',')
    tags = {}
    tags["Référence Données"] = values_tags[0]
    tags["Version des données"] = values_tags[1]
    tags["Niveau"] = values_tags[2]
    tags["Date"] = values_tags[3]
    tags["Copyright"] = values_tags[4]
    tags["Source Logicielle"] = values_tags[5]
    tags["Source Matérielle"] = values_tags[6]
    tags["Description"] = values_tags[7].replace(" ", "_")

    # Récupération du token, organisation, bucket et url pour Influxdb
    token = config.token_influxdb
    org = config.org_influxdb
    url = config.url_influxdb

    # Connection Influxdb
    client = InfluxDBClient(url=url, token=token, debug=True)
    write_api = client.write_api(write_options=SYNCHRONOUS)

    for index, line in df.iterrows():
        # Parsing date timestamp to date milliseconds
        date = line[0].replace('t', " ")
        date = date.replace('T', " ")
        date = date.replace('Z', "")
        date = date.replace('z', "")
        date = date.replace('.000', "")
        date = date.replace('-', "/")
        datetime_object = datetime.datetime.strptime(date, '%d/%m/%Y %H:%M:%S')
        date_milliseconds = int(
            round(datetime_object.timestamp() * 1000000000))
        history_data(process_type, swift_container, swift_id,
                    "parsing_date_timestamp_to_date_milliseconds", line[0], date_milliseconds)
        new_data = []
        values = {}
        for key, value in enumerate(line[1:]):
            dt = []
            value = float(value)            
            values["value"] = value
            # Create variable for upload in influxdb
            dt.append(
                {
                    "measurement": columns[key+1],
                    "tags": tags,
                    "fields": values,
                    "time": date_milliseconds
                }
            )
            result.append(dt)
            # Upload in influxdb
            write_api.write(swift_container, org, dt, protocol='json')
    return result


sys.modules[__name__] = extract_transform_load_time_series_text
