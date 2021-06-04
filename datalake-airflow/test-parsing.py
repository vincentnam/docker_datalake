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
lines = csv_file.split("\n") # "\r\n" if needed

columns = lines[0].split(",")

def get_position_timestamp(columns, timestamp_fields_list, value_fields_list):
    position_timestamp = -1
    position_value = -1
    for key, value in enumerate(columns):
        value = value.replace('"', '')
        if value in timestamp_fields_list :
            position_timestamp = key
        if value in value_fields_list :
            position_value = key

    return position_timestamp, position_value

position_timestamp, position_value = get_position_timestamp(
    columns, 
    timestamp_fields_list, 
    value_fields_list
)
print(position_timestamp)
print(position_value)

from datetime import datetime

from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS

# You can generate a Token from the "Tokens Tab" in the UI
token = "TOKEN"
org = "ORG"
bucket = "BUCKET"

client = InfluxDBClient(url="http://IP_ADDRESS:PORT", token=token, debug=True)
write_api = client.write_api(write_options=SYNCHRONOUS)

for line in lines[1:]:
    if line != "": # add other needed checks to skip titles
        cols = line.split(",")

        result_row = {
            #"time" : cols[position_timestamp].replace('"', '') if position_timestamp != -1 else '', 
            "time": 1465839830100400200,
            "tags": { "user": "Nikhil" },  \
            "measurement": "test",
            "fields" : {
                "value": cols[position_value].replace('"', '') if position_value != -1 else ''
            }
        }

        point = Point("mem") \
            .tag("host", "host1") \
            .field("used_percent", 23.43234543) \
            .time(datetime.utcnow(), WritePrecision.NS)

        write_api.write(bucket, org, point)

        result.append(result_row)

'''ip_address = "IP_ADDRESS"

client = InfluxDBClient(ip_address, 8086, 'admin', 'admin')'''

def register_influxdb(data):
    return True