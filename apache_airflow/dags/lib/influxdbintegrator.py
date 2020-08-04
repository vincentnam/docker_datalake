from influxdb_client import InfluxDBClient, Point

class InfluxIntegrator:
    def __init__(self, influx_host="141.115.103.33", influx_port=8086,
                 **kwargs):
        self.influx_client = InfluxDBClient(url="http://"+influx_host +
                                                ":"+str(influx_port), **kwargs)
        # Default write option is Batching
        self.write_api = self.influx_client.write_api()
        self.query_api = self.influx_client.query_api()
        # self.database_list = self.influx_client.get_list_database()


    def write(self,bucket,measurement : str,
              time ,
              field_list : list,
              tag_list : list = [],
              **kwargs):
        '''
        :param bucket : the bucket on which write the data
        :param measurement: name of measurement
        :param time: timestamp
        :param field_list: field list : containing tuple (key,value)
        :param tag_list: tag_lisit : containing tuple (key,value)
        optionnal parameter
        :return:
        '''
        point = Point(measurement)
        point.time(time)
        if not field_list :
            # TODO : Create an exception NoDataException
            raise Exception("Not point to write in database.")
        for field_tuple in field_list:
            point.field(field_tuple[0],field_tuple[1])
        for tag_tuple in tag_list:
            point.tag(tag_tuple[0], tag_tuple[1])

        self.write_api.write(bucket=bucket, record=point, **kwargs)



#
#
# class InfluxIntegrator:
#     def __init__(self, influx_host="141.115.103.33", influx_port=8086, **kwargs):
#         self.influx_client = InfluxDBClient(host=influx_host, port=influx_port,
#                                             **kwargs)
#         self.database_list = self.influx_client.get_list_database()
#
#     def write(self, points: list, db: str):
#         '''
#
#         :param points:
#         :param db:
#         :return: bool : return status : true if successful
#         '''
#         if db not in self.database_list:
#             self.influx_client.create_database(dbname=db)
#         self.influx_client.switch_database(db)
#         # TODO : Set authentications (user / password)
#         if self.influx_client.write_points(points):
#             print("Data have been written to InfluxDB.")
#             return True
#         else :
#             raise Exception("Failed write in Influx database : %s", db)
#
#     def mongodoc_to_influx(self, json):
#         if "payload" in json:
#             return {
#                 "measurement": json["payload"]["value_units"],
#                 "tags": {
#                     "subID" : json["payload"]["subID"],
#                     "input" : json["payload"]["input"]
#                 },
#                 "time": json["date"],
#                 "fields": {
#                     "value" : json["payload"]["value"],
#                 }
#             }
#         elif "data" in json :
#             if "payload" in json["data"]:
#                 return {
#                     "measurement": json["data"]["payload"]["value_units"],
#                     "tags": {
#                         "subID" : json["data"]["payload"]["subID"],
#                         "input" : json["data"]["payload"]["input"]
#                     },
#                     "time": json["data"]["date"],
#                     "fields": {
#                         "value" : json["data"]["payload"]["value"],
#                     }
#                 }
#             else:
#                 return {}
#         else:
#             return {}
