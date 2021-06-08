import pandas as pd
import sys

f = open("sensors.csv", "r")

from influxdb import InfluxDBClient

result = []
timestamp_fields_list = [
    "timestamp",
    "temps",
    "date",
    "measuretime"
]

value_fields_list = [
    "value",
    "valeur",
    "reading",
    "payload.value"
]

def is_in_line(field_name):
    res = False
    if field_name in timestamp_fields_list:
        res = True
    return res

csv_file = f.read()
if sys.version_info[0] < 3: 
    from StringIO import StringIO
else:
    from io import StringIO

data = StringIO(csv_file)

df = pd.read_csv(data, sep=",")
columns = df.columns

def get_position_timestamp(columns, timestamp_fields_list, value_fields_list):
    position_timestamp = ""
    position_value = ""
    position_topic = ""
    position_payload_value_units = ""
    for key, value in enumerate(columns):
        if value in timestamp_fields_list :
            position_timestamp = value
        if value in value_fields_list :
            position_value = value
        if value == "topic":
            position_topic = value
        if value == "payload.value_units":
            position_payload_value_units = value

    return position_timestamp, position_value, position_topic, position_payload_value_units

position_timestamp, position_value, position_topic, position_payload_value_units = get_position_timestamp(
    columns, 
    timestamp_fields_list, 
    value_fields_list
)


from datetime import datetime

from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS

# You can generate a Token from the "Tokens Tab" in the UI
token = "TOKEN"
org = "ORG"
bucket = "BUCKET"

client = InfluxDBClient(url="URL", token=token, debug=True)
write_api = client.write_api(write_options=SYNCHRONOUS)

for index, line in df.iterrows():
    date = line[position_timestamp].replace('T', " ")
    date = date.replace('Z', "")
    date = date.replace('.000', "")
    date = date.replace('-', "/")
    datetime_object = datetime.strptime(date, '%Y/%m/%d %H:%M:%S')
    date_milliseconds = int(round(datetime_object.timestamp() * 1000000000))
    data = []
    values = {}
    tags = {}
    if "energy" not in line[position_topic]:
        val = float(line[position_value])
        values[line[position_payload_value_units]] = val
    else:
        list_of_tuples = list(zip(line[position_payload_value_units].strip('][').split(','), line[position_value].strip('][').split(',')))
        for l in list_of_tuples:
            unit, v = l
            values[unit] = float(v)
    for key, value in enumerate(columns):
        if position_payload_value_units != value and position_value != value:
            if line[value] == "":
                tags[value] = ""
            else:
                tags[value] = str(line[value])
    data.append(
        {
            "measurement": line[position_topic],
            "tags": tags,
            "fields": values,
            "time": date_milliseconds
        }
    )
        
    write_api.write(bucket, org, data, protocol='json')            
                
                
                
def register_influxdb(data):
    return True