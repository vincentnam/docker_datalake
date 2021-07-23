import sys
import json
from datetime import datetime
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS
import config


def extract_transform_load_time_series_json(swift_result):
    """
    Fonction de traitement d'un fichier Json Time Series
    """
    client = InfluxDBClient(url=config.url_influxdb, token=config.token_influxdb)
    write_api = client.write_api(write_options=SYNCHRONOUS)

    time_format = "%Y-%m-%dT%H:%M:%S.%fZ"
    points = []
    for m in json.loads(swift_result):
        topic = m.get("topic")
        subID = m.get("subID")
        unitID = m.get("unitID")
        input_v = m.get("input")
        value_units = m.get("value_units")
        value = m.get("value")
        time = datetime.strptime(m.get("time"), time_format)

        if "energy" in topic:
            if config.influxdb_measurement == "topic":
                point = Point(topic) \
                    .tag("subID", subID) \
                    .tag("unitID", unitID) \
                    .time(time, WritePrecision.MS)
                if "input" in m:
                    point.tag("input", input_v)
                for i in range(len(value_units)):
                    point.field(value_units[i], value[i])
                points.append(point)
            else:
                for i in range(len(value_units)):
                    point = Point(value_units[i]) \
                        .field("value", value[i]) \
                        .tag("topic", topic) \
                        .tag("subID", subID) \
                        .tag("unitID", unitID) \
                        .time(time, WritePrecision.MS)
                    if "input" in m:
                        point.tag("input", input_v)
                    points.append(point)
        else:
            if config.influxdb_measurement == "topic":
                point = Point(topic) \
                    .field(value_units, value)
            else:
                point = Point(value_units) \
                    .field("value", value) \
                    .tag("topic", topic)

            point.tag("subID", subID) \
                .tag("unitID", unitID) \
                .time(time, WritePrecision.MS)

            if "input" in m:
                point.tag("input", input_v)

            points.append(point)

    write_api.write(config.bucket_influxdb, config.org_influxdb, points)


sys.modules[__name__] = extract_transform_load_time_series_json
