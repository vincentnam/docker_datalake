from influxdb import InfluxDBClient


class InfluxIntegrator:
    def __init__(self, influx_host="influxdb_gold", influx_port=8086, **kwargs):
        self.influx_client = InfluxDBClient(host=influx_host, port=influx_port,
                                            **kwargs)
        self.database_list = self.influx_client.get_list_database()

    def write(self, points: list, db: str):
        '''

        :param points:
        :param db:
        :return: bool : return status : true if successful
        '''
        if db not in self.database_list:
            self.influx_client.create_database(dbname=db)
        self.influx_client.switch_database(db)
        # TODO : Set authentications (user / password)
        if self.influx_client.write_points(points):
            return True
        else :
            raise Exception("Failed write in Influx database : %s", db)

    def mongodoc_to_influx(self, json):
        if "payload" in json:
            return {
                "measurement": json["payload"]["value_units"],
                "tags": {
                    "subID" : json["payload"]["subID"],
                    "input" : json["payload"]["input"]
                },
                "time": json["date"],
                "fields": {
                    "value" : json["payload"]["value"],
                }
            }
        elif "data" in json :
            if "payload" in json["data"]:
                return {
                    "measurement": json["data"]["payload"]["value_units"],
                    "tags": {
                        "subID" : json["data"]["payload"]["subID"],
                        "input" : json["data"]["payload"]["input"]
                    },
                    "time": json["data"]["date"],
                    "fields": {
                        "value" : json["data"]["payload"]["value"],
                    }
                }
            else:
                return {}
        else:
            return {}
