import sys
from pymongo import MongoClient
from services import insert_anomaly, get_all_measurements, insert_anomaly
from datetime import datetime, timedelta
from influxdb_client import InfluxDBClient
import config
import json

#Fonction de récupération des anomalies dans influxdb
def get_anomaly(Jour_1, Jour_2, container_name):
    # Récupération du token, organisation, bucket et url pour Influxdb
    token = config.token_influxdb
    org = config.org_influxdb
    url = config.url_influxdb

    #Connection Influxdb
    client = InfluxDBClient(url=url, token=token, debug=True, verify_ssl=False)

    bucket = container_name
    startDate = (datetime.now() - timedelta(days = Jour_2) ).isoformat() + "Z"
    endDate = (datetime.now() - timedelta(days=Jour_1) ).isoformat() + "Z"

    measurements = get_all_measurements(bucket)


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
    anomaly = {
        "anomaly" : last_anomaly
    }

    result = insert_anomaly(anomaly,endDate, container_name)
    return None


sys.modules[__name__] = get_anomaly