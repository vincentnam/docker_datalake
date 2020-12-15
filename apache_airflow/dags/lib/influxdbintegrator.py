from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS
class InfluxIntegrator:
    def __init__(self, influx_url="http://141.115.103.33:8086",
                 token = None, org=None, **kwargs):
        self.org = org
        self.token = token
        self.influx_client = InfluxDBClient(url=influx_url, token=token, org=org, **kwargs)
        # Default write option is Batching
        self.write_api = self.influx_client.write_api(write_options=SYNCHRONOUS)
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
        point.time(time,WritePrecision.MS)
        if not field_list :
            # TODO : Create an exception NoDataException
            raise Exception("Not point to write in database.")
        for field_tuple in field_list:
            point.field(field_tuple[0],field_tuple[1])
        for tag_tuple in tag_list:
            point.tag(tag_tuple[0], tag_tuple[1])

        self.write_api.write(bucket=bucket, record=point, org= self.org, **kwargs)


    def write_dataframe(self,df, bucket,measurement : str,
              time ,
              tag_list : list = [],
              **kwargs):
        self.write_api.write(bucket, record=df, org= self.org,
                             data_frame_measurement_name = measurement, data_frame_tag_columns = tag_list)


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


    #  READ CSV !!

    # def parse_row(row):
    #
    #     list_field = ["pmer", "tend", "cod_tend", "dd", "ff", "t", "td", "u", "vv", "ww", "w1", "w2", "n", "nbas",
    #                   "hbas", "cl", "cm", "ch",
    #                   "pres", "niv_bar", "geop", "tend24", "tn12", "tn24", "tx12", "tx24", "tminsol", "sw", "tw",
    #                   "raf10", "rafper", "per"
    #         , "etat_sol", "ht_neige", "ssfrai", "perssfrai", "rr1", "rr3", "rr6", "rr12", "rr24", "phenspe1",
    #                   "phenspe2", "phenspe3",
    #                   "phenspe4", "nnuage1", "ctype1", "hnuage1", "nnuage2", "ctype2", "hnuage2", "nnuage3", "ctype3",
    #                   "hnuage3", "nnuage4",
    #                   "ctype4", "hnuage4"]
    #     print(datetime.datetime.strptime(str(row['date']), "%Y%m%d%H%M%S"))
    #     point = Point("MeteoFrance_data") \
    #         .tag("station", row["numer_sta"]) \
    #         .time(datetime.datetime.strptime(str(row['date']), "%Y%m%d%H%M%S"), write_precision=WritePrecision.S)
    #     for field in list_field:
    #         if row[field] != "mq":
    #             point.field(field, float(row[field]))
    #     return point
    # token = "jr_IXluKJloga_xbkMTaadVu_IZGCODrqtNgtFJ9HCKZR7-ndrMXYyDWSAKvU0qQcrnWur0WdNaeTK1xzr7clQ=="
    # org="test"
    # bucket="DataNoos"
    #
    # data = rx \
    #     .from_iterable(DictReader(open('synop.202011.csv', 'r'))) \
    #     .pipe(ops.map(lambda row: parse_row(row)))
    #
    # client = InfluxDBClient(url="http://localhost:9999", token=token, org=org, debug=True)
    #
    # """
    # Create client that writes data in batches with 50_000 items.
    # """
    # write_api = client.write_api(write_options=WriteOptions(batch_size=1000, flush_interval=100))
    #
    # """
    # Write data into InfluxDB
    # """
    # write_api.write(bucket=bucket, record=data)
    # write_api.__del__()