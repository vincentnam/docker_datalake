import sys

from bson import ObjectId
from pymongo import MongoClient


import datetime
import logging
import json
from dateformating import format_date
import jsontools

class MongoTools:
    def __init__(self, mongouri, database_name, coll_name, start_id = None, start_date=None):
        self.mongouri = mongouri
        self.coll_name = coll_name
        self.database_name = database_name
        self.MongoClient = MongoClient(mongouri)[database_name]
        self._start_id = start_id
        self._start_date =  format_date(start_date)
        self.log = logging.getLogger(self.__class__.__name__)
        self.overall_processed = 0

    # TODO : tools to transform MongoDB dump to JSON list of documents
    def load(self):
        self.log.debug("[LOAD] legacy_processor is preparing ...")

        # extract sensors id list from mongoDB
        sensorID_list = dict()
        try:
            _iter = self.MongoClient.typecapteur.find()
            # parse 'typecapteur' collection (e.g temperature, co2, humidity etc etc)
            for document in _iter:
                # parse sensors: each sensor has an ID
                # key nomCapteur: <topic/unitID/subID> e.g u4/campusfab/temperature/auto_92F8/79
                #   value = list( id associated with <topic/unitID/subID>, id piece )
                for capteur_doc in document["Capteurs"]:
                    sensorID_list[capteur_doc["idCapteur"]] = capteur_doc[
                        "nomCapteur"]
        except Exception as e:
            self.log.warning("while getting list of capteur " + str(e))

        print("sensorID: " + str(sensorID_list))

        # mongodb filter
        _mongo_filter = dict()
        # | start_id
        if (self._start_id is not None):
            try:
                _mongo_filter['_id'] = {"$gte": ObjectId(self._start_id)}
            except Exception as ex:
                self.log.warning(
                    "while creating mongoDB filter from _id: " + str(ex))

                sys.exit(1)
        # | start_date
        elif (self._start_date is not None):
            try:
                # generate an id from data
                # [apr.20] there exist a two hours shift between ObjectId time and real utc measuretime ?!?!
                _mongo_filter['_id'] = {
                    "$gte": ObjectId.from_datetime(self._start_date)}
            except Exception as ex:
                self.log.warning(
                    "while creating mongoDB filter from _id: " + str(ex))
                # self._shutdownEvent.set()
                sys.exit(1)

        # generate mongoDB iterator

        _src_iterator = self.MongoClient[self.coll_name].find(
            _mongo_filter)
        # _src_iterator = self._src.find( self._collection_name, query=_mongo_filter, skip=1000000 )

        # generate importer iterator
        cur_iter = dict()
        cur_iter['sensorID'] = sensorID_list
        cur_iter['iterators'] = [_src_iterator]

        self.overall_processed = 0
        print(_src_iterator[0])
        # log.info("MongoDB connection is UP featuring:\n\t{0:,d} measures :)\n\t{1:,d} unmanaged measures :(".format(mydb.measure.count(),mydb.failedData.count()) )

        return cur_iter


    def neocampus_data_processing(self, doc):
        # 1: DATA TIME
        try :

            if('device' in doc.keys()):
                device = doc["device"]
            else:
                raise Exception("No device field found : no measurement type")

            _measureTime = None
            if ('datemesure' in doc.keys()):
                _measureTime = doc['datemesure']
            elif ('date' in doc.keys()):
                _measureTime = doc['date']
            else:
                raise Exception("no time of measure found ?!?!")

            # print( _measure )
            # _dataTime = _measure['_id'].generation_time  [apr.20] not UTC ?!?!
            # _uri = cur_iter['sensorID'][ _measure['idcapteur'] ]
            # _value = _measure['mesurevaleur'][0]['valeur']
            # if( str(_value).lower() == "nan" ): continue

            if (isinstance(_measureTime, str)):
                _dataTime = datetime.fromisoformat(_measureTime)
            elif (isinstance(_measureTime, datetime.datetime)):
                _dataTime = _measureTime
            else:
                raise Exception("unsupported 'datemesure' format !")

            # 2: TOPIC
            if ('topic' in doc.keys()):
                _uri = doc['topic']
            elif ('uri' in doc.keys()):
                _uri = doc['uri']
            # else:
                # extract from sensorIDs
                # _uri = cur_iter['sensorID'][_measure['idcapteur']]

            _topicTokens = _uri.split('/')[:3]

            topic = "/".join(_topicTokens)

            # FAILEDDATA collection filter
            # if( 'energy' in topic ): continue
            # if( 'digital' in topic ): continue
            # if( topic.startswith('bu') is not True or topic.endswith('temperature') is not True ): continue

            # if( 'shutter' not in topic ): continue

            # 3: PAYLOAD
            if ('payload' in doc.keys()):
                payload = doc['payload']
            elif ('data' in doc.keys()):
                payload = doc['data']['payload']
            elif ('mqtt_data' in doc.keys()):
                payload = doc['mqtt_data']['payload']
            else:
                # further processing needed
                raise Exception("no payload found ?!?!")

            if (isinstance(payload, str)):
                # import json dump
                try:
                    payload = json.loads(payload.decode('utf-8'))
                except Exception as ex:
                    payload = json.loads(payload)
            print(_dataTime)
            return device,_dataTime, _uri, payload
        except Exception as e :
            #TODO : save error doc id
            pass

if __name__ == "__main__":
    import influxdbintegrator
    mongotool = MongoTools("mongodb://localhost:27017","neocampus","measure", start_date="2018-01-01")
    mongoset = mongotool.load()
    data_point = set([])
    aux= 0
    influxd= influxdbintegrator.InfluxIntegrator(influx_url="http://localhost:9999",
                                                 token="nfd23prECgPsUjNkwPZ95L6sw74u5dNAwUy2ChMp9giyD_Bor7Hbnvp3W1hMaqN2Qrk0J_oyaIUtpZpcEXcohQ==",
                                                 org="test")
    for i in mongoset["iterators"][0] :
        # print(i)
        try:
            point = jsontools.mongodoc_to_influx_list(
                mongotool.neocampus_data_processing(i))
            point['time'] =point['time']
            print(point)

            influxd.write(bucket="test",
                          measurement=point["measurement"],
                          time = point["time"], field_list=point["fields"],
                           tag_list=point["tags"])
            print(aux)
            aux+=1
            # PROBLEME : création des points : measurements pas bon ?
            if aux == 300000:
                break
        except :
            continue

    # import influxdb_client
    # from influxdb_client import InfluxDBClient, Point, WritePrecision
    #
    # client = InfluxDBClient(url="http://localhost:9999", token="rJ1fDpYDP3ElLO-FesJtfmu-p_f4jo8NHRLR3-6elKbQHVvyAgONZwNoa_1xX2kK3qml-LJIyHQ4UasH8FoqHw==")
    # write_api = client.write_api()
    # point = Point("mem") \
    #     .tag("host", "host1") \
    #     .field("used_percent", 23.43234543) \
    #     .time(1556896326, WritePrecision.NS)
    # write_api.write("test", "admin", point)

