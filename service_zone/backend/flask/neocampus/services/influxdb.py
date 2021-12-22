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
    client = InfluxDBClient(url=current_app.config['INFLUXDB_URL'], token=token, debug=True)

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
        f'''from(bucket:"{current_app.config['INFLUXDB_BUCKET']}")  
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
    client = InfluxDBClient(url=url, token=token, debug=True)
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

def get_data_anomaly(Jour_1, Jour_2) :
    """
    get_data_anomaly from influxdb between 2 dates 
    :param Jour_1:  
    :param Jour_2:
    :return: Anomaly (dict)
    """
    client, org = influxdb.connection_inflxdb()

    bucket = "neOCampus"
    startDate = (datetime.now() - timedelta(days = Jour_2) ).isoformat() + "Z"
    endDate = (datetime.now() - timedelta(days=Jour_1) ).isoformat() + "Z"
    
    measurements = influxdb.get_all_measurements(bucket)
    anomalies = []
    # Execute the query
    query_api = client.query_api()
    for measurement in measurements :
        tables = query_api.query(f'''
        from(bucket: \"{bucket}\") |> range(start: {startDate}, stop: {endDate})
            |> filter(fn: (r) => r["_measurement"] == \"{measurement}\")
            |> group(columns: ["topic"])
        ''', org=org)
        topics = []
        # Parsing the result for return the list of topics
        for table in tables:
            for record in table.records:
                # Verification if the topic is in the list
                if record.values.get("topic") not in topics:
                    topics.append(str(record.values.get("topic")))

        all_topics = {
            "topics": topics
        }
        for topic in all_topics["topics"] :
            result = query_api.query_data_frame(f'''
            from(bucket: \"{bucket}\")
                |> range(start: {startDate}, stop: {endDate})
                |> filter(fn: (r) => r["_measurement"] == \"{measurement}\" and r["topic"] == \"{topic}\")
                |> group(columns: ["_time"])
            ''', org=org)

            #Dataframe to json format
            data = result.to_json(orient="index")
            data = json.loads(data)
            all_data = []
            for key, value in data.items() :
                all_data.append(value)

            for data in all_data :
                if data["_value"] == 0 :
                    new_anomaly_1 = {   
                        "topic": topic,
                        "value": int(data["_value"]),
                        "unit": measurement,
                        "datetime": data["_time"]/1000 - 86400, 
                        "startDate_detection": startDate,
                        "endDate_detection": endDate,
                        "nbr" : 1
                    }
                    new_anomaly_2 = {   
                        "topic": topic,
                        "value": int(data["_value"]),
                        "unit": measurement,
                        "datetime": data["_time"]/1000 - 172800,
                        "startDate_detection": startDate,
                        "endDate_detection": endDate,
                        "nbr" : 2
                    }
                    if new_anomaly_1 in anomalies :
                        anomalies.append(
                            {   
                                "topic": topic,
                                "value": int(data["_value"]),
                                "unit": measurement,
                                "datetime": data["_time"]/1000 - 86400,
                                "startDate_detection": startDate,
                                "endDate_detection": endDate,
                                "nbr" : 2
                            }
                        )
                    elif new_anomaly_2 in anomalies :
                        anomalies.append(
                            {   
                                "topic": topic,
                                "value": int(data["_value"]),
                                "unit": measurement,
                                "datetime": data["_time"]/1000 - 172800,
                                "startDate_detection": startDate,
                                "endDate_detection": endDate,
                                "nbr" : 3
                            }
                        )
                    else :
                        anomalies.append(
                            {   
                                "topic": topic,
                                "value": int(data["_value"]),
                                "unit": measurement,
                                "datetime": data["_time"]/1000,
                                "startDate_detection": startDate,
                                "endDate_detection": endDate,
                                "nbr" : 1
                            })
    print(anomalies)
    last_anomaly =[]
    for ano in anomalies :
        if ano['nbr'] == 3 : 
            last_anomaly.append(
                {   
                                "topic": ano['topic'],
                                "value": int(ano["value"]),
                                "unit": ano['unit'],
                                "datetime": str(datetime.fromtimestamp(ano["datetime"]).strftime("%Y-%m-%dT%H:%M:%S.%fZ")),
                                "startDate_detection": startDate,
                                "endDate_detection": endDate,
                            }
            )
    print(last_anomaly)
    anomaly = {
        "anomaly" : last_anomaly
    }

    result = mongo.insert_anomaly(anomaly,endDate)
    #print("for influx db")
    #print(anomaly)
    return anomaly