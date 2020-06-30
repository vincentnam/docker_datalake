from influxdb import InfluxDBClient


class InfluxIntegrator:
    def __init__(self, influx_host="influxdb_gold", influx_port=8086, **kwargs):
        self.influx_client = InfluxDBClient(host=influx_host, port=influx_port,
                                            **kwargs)
        self.database_list = self.influx_client.get_list_database()

    def write(self, points: dict, db: str):
        if db not in self.database_list:
            self.influx_client.create_database(dbname=db)
        self.influx_client.switch_database(db)
        # TODO : Set authentications (user / password)
        return self.influx_client.write_points(points)
