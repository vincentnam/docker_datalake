import sys
from pymongo import MongoClient
from influxdb_client import InfluxDBClient
import config

#Fonction de récupération des measurements d'un bucket
def get_all_measurements(bucket):
    # Récupération du token, organisation, bucket et url pour Influxdb
    token = config.token_influxdb
    org = config.org_influxdb
    url = config.url_influxdb

    #Connection Influxdb
    client = InfluxDBClient(url=url, token=token, debug=True, verify_ssl=False)
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

sys.modules[__name__] = get_all_measurements