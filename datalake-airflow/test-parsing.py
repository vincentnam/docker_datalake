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
    position_topic = -1
    for key, value in enumerate(columns):
        value = value.replace('"', '')
        if value in timestamp_fields_list :
            position_timestamp = key
        if value in value_fields_list :
            position_value = key
        if value == "topic":
            position_topic = key

    return position_timestamp, position_value, position_topic

position_timestamp, position_value, position_topic = get_position_timestamp(
    columns, 
    timestamp_fields_list, 
    value_fields_list
)

from datetime import datetime

from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS

# You can generate a Token from the "Tokens Tab" in the UI
token = "Token"
org = "ORG"
bucket = "BUCKET"

client = InfluxDBClient(url="URL", token=token, debug=True)
write_api = client.write_api(write_options=SYNCHRONOUS)

for line in lines[1:]:
    if line != "":
        # add other needed checks to skip titles
        cols = line.replace("'", "")
        cols = cols.replace('""', "'")
        cols = line.split('","')
        result = []
        for col in cols:
            
            val = col.replace('"', '')

            val = val.replace('(', "('")
            val = val.replace(')', "')")
            val = col
            result.append(val)
        print(result)
        # result_row = {
        #     #"time" : "", 
        #     "time": 1465839830100400200,
        #     "tags": { "user": "influxdb" },  \
        #     "measurement": "test",
        #     "fields" : {
        #         "value": cols[position_value].replace('"', '') if position_value != -1 else ''
        #     }
        # }
        # firstcaracter = result[position_value][0]
        # # print(firstcaracter)
        # if  firstcaracter == "[":
        #     res = result[position_value].replace('[', '')
        #     res = float(res)
        # else:
        #     
        
        if result[position_topic] != "energy":
            res = float(result[position_value])
            date = result[position_timestamp].replace('T', " ")
            date = date.replace('Z', "")
            print(datetime.utcnow())
            point = Point(result[position_topic]) \
                .tag("topic", result[position_topic]) \
                .field(result[position_topic+1], res) \
                .time(date, WritePrecision.NS)
        

        write_api.write(bucket, org, point)

        result.append(result)

'''ip_address = "IP_ADDRESS"

client = InfluxDBClient(ip_address, 8086, 'admin', 'admin')'''

def register_influxdb(data):
    return True