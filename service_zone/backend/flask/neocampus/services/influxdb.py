from flask import current_app
from influxdb_client import InfluxDBClient, Dialect

def get_handled_data():
    #Connection Influxdb
    token = "zQZd3Q-5sV0jKKFCXKMoSYd1AqK0HjMX8UFEueLa5lIa76uNch4hsISB0mvL_USZMuhp-rtg9HDOBYv3OpNpuQ=="
    org = "modis"

    # Connection to InfluxDB database
    client = InfluxDBClient(url=current_app.config['INFLUX_URL'], token=token, debug=True)

    # Query
    query_api = client.query_api()

    """
    Query: using csv library
    1st parameter : query,
    2nd parameter : Dialect instance (object) to specify details / options about CSV result
    3rd parameter : org (for organization)

    All informations above have been copied from InfluxDB UI : Telegraf 
    """
    csv_result = query_api.query_csv(
        'from(bucket:"test2") |> range(start: -30d)',
        dialect=Dialect(
            header=True, 
            delimiter=",", 
            comment_prefix="#", 
            annotations=[],
            date_time_format="RFC3339"
        ), 
        org=org
    )

    return csv_result