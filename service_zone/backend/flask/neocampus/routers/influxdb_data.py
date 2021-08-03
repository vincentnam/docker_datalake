from flask import Blueprint, jsonify, request, current_app
from influxdb_client import InfluxDBClient
from ..services import influxdb
from datetime import datetime
import json

influxdb_data_bp = Blueprint('influxdb_data_bp', __name__)


@influxdb_data_bp.route('/bucket', methods=['GET'])
def get_all_buckets():
    client, org = influxdb.connection_inflxdb()
    buckets_api = client.buckets_api()
    buckets = buckets_api.find_buckets().buckets
    list_buckets = []

    for bucket in buckets:
        list_buckets.append(bucket.name)

    all_buckets = {
        "buckets": list_buckets
    }
    return jsonify(all_buckets)


@influxdb_data_bp.route('/measurements', methods=['GET', 'POST'])
def get_all_measurements():
    client, org = influxdb.connection_inflxdb()
    bucket = request.get_json()["bucket"]
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

    all_measurements = {
        "measurements": measurements
    }
    return jsonify(all_measurements)


@influxdb_data_bp.route('/topics', methods=['GET', 'POST'])
def get_all_topics():
    client, org = influxdb.connection_inflxdb()
    bucket = request.get_json()["bucket"]
    measurement = request.get_json()["measurement"]
    tag = "topic"
    # Execute the query
    query_api = client.query_api()
    tables = query_api.query(f'''
    from(bucket: \"{bucket}\") |> range(start: 2021-01-01T00:00:00Z)
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
    return jsonify(all_topics)


@influxdb_data_bp.route('/dataTimeSeries', methods=['GET', 'POST'])
def get_data_time_series():
    client, org = influxdb.connection_inflxdb()
    bucket = request.get_json()["bucket"]
    measurement = request.get_json()["measurement"]
    topic = request.get_json()["topic"]
    startDate = request.get_json()["startDate"]
    endDate = request.get_json()["endDate"]
    # Execute the query
    query_api = client.query_api()
    result = query_api.query_data_frame(f'''
    from(bucket: \"{bucket}\")
        |> range(start: {startDate}, stop: {endDate})
        |> filter(fn: (r) => r["_measurement"] == \"{measurement}\" and r["topic"] == \"{topic}\")
        |> group(columns: ["_time"])
    ''', org=org)
    
    #Dataframe to json format
    data = result.to_json(orient="index")
    data = json.loads(data)
    dataGraph = result.to_json()
    dataGraph = json.loads(dataGraph)
    all_topics = {
        "dataTimeSeries": [data],
        "dataTimeSeriesGraph": [dataGraph]
    }
    return jsonify(all_topics)
