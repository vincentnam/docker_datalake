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

csv_file = f.read()
if sys.version_info[0] < 3: 
    from StringIO import StringIO
else:
    from io import StringIO

# print(csv_file)
file = b'"_id","measuretime","topic","payload.value","payload.value_units","payload.input","payload.subid","payload.unitid"\\n"objectid(""60606b525ebb635c20b5d687"")","2021-03-28t11:41:06.000z","u4/302/energy","[246078,246070,234.27,0.12,10,30,30,0.2]","[""wh"",""ea+"",""v"",""a"",""w"",""var"",""va"",""cosphi""]",88,"prises1","modbus_rs485"\\n"objectid(""60606b525ebb635c20b5d688"")","2021-03-28t11:41:06.000z","u4/302/energy","[7061178,7061170,234.1,0.78,110,150,180,0.61]","[""wh"",""ea+"",""v"",""a"",""w"",""var"",""va"",""cosphi""]",65,"prises2","modbus_rs485"\\n"objectid(""60606b525ebb635c20b5d689"")","2021-03-28t11:41:06.000z","u4/302/energy","[3090025,3090020,233.94,0.28,40,50,70,0.62]","[""wh"",""ea+"",""v"",""a"",""w"",""var"",""va"",""cosphi""]",62,"prises3","modbus_rs485"\\n"objectid(""60606b535ebb635c20b5d68a"")","2021-03-28t11:41:07.000z","irit2/366/energy","[533558,533550,234.3,0.09,10,20,20,0.53]","[""wh"",""ea+"",""v"",""a"",""w"",""var"",""va"",""cosphi""]",61,"main","modbus_rs485"\\n"objectid(""60606b555ebb635c20b5d68b"")","2021-03-28t11:41:09.000z","u4/campusfab/luminosity",249,"lux",,57,"auto_2c76"\\n"objectid(""60606b575ebb635c20b5d68c"")","2021-03-28t11:41:11.000z","u4/300/luminosity",205,"lux",100,"ilot1","inside"\\n"objectid(""60606b575ebb635c20b5d68d"")","2021-03-28t11:41:11.000z","u4/300/luminosity",299,"lux",105,"ilot2","inside"'
s=str(file,'utf-8').replace("\\n", "\n")

# s = s.split('\\n')
# with open('csvfile.csv','w') as fi:
#     for line in s:
#         fi.write(line)
#         fi.write('\n')
# f = open("csvfile.csv", "r")
# fl = f.read()

data = StringIO()
data.write(s)
data.seek(0)
df = pd.read_csv(data, sep=",")
print(df)
columns = df.columns

def get_positions(columns, timestamp_fields_list, value_fields_list):
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

position_timestamp, position_value, position_topic, position_payload_value_units = get_positions(
    columns, 
    timestamp_fields_list, 
    value_fields_list
)


from datetime import datetime

from influxdb_client import InfluxDBClient
from influxdb_client.client.write_api import SYNCHRONOUS

# You can generate a Token from the "Tokens Tab" in the UI
token = "ILcRQADkRgQSuVQB_rl-zU6m9XDh9EiUGxoHgLkspvQuYAU5aWGJMnK8dCwYaQmdLuXTZn2qVvNDh4tMfFg1qA=="
org = "modis"
bucket = "test"

client = InfluxDBClient(url="http://neocampus-datalake-mongodb.dev.modiscloud.net:8086", token=token, debug=True)
write_api = client.write_api(write_options=SYNCHRONOUS)

for index, line in df.iterrows():
    date = line[position_timestamp].replace('t', " ")
    date = date.replace('z', "")
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
    print(data)
    write_api.write(bucket, org, data, protocol='json')            
                
                
                
def register_influxdb(data):
    return True