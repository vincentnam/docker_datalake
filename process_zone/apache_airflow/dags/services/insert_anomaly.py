import sys
from pymongo import MongoClient
import config
import datetime

#Fonction de d'insertion dans mongo des anomaly
def insert_anomaly(anomaly,endDate,container_name):
    mongodb_url = config.mongodb_url
    anomalie = anomaly
    mongo_client = MongoClient(mongodb_url, connect=False).data_anomaly.influxdb_anomaly
    data_histor = mongo_client.find({ "container_name": container_name })
    new_date = endDate #datetime.datetime.now().isoformat() + "Z"

    for ano in anomalie["anomaly"] :
        ano["startDate_detection"] = datetime.datetime.strptime(str(ano["startDate_detection"]), "%Y-%m-%dT%H:%M:%S.%fZ")
        ano["endDate_detection"] = datetime.datetime.strptime(str(ano["endDate_detection"]), "%Y-%m-%dT%H:%M:%S.%fZ")
        ano['datetime'] = datetime.datetime.strptime(ano['datetime'], "%Y-%m-%dT%H:%M:%S.%fZ")

    anomaly_without_id =[]
    data_without_id = {'objects': []}
    for row in data_histor:
        data_without_id['objects'].append({
            "topic": row['topic'],
            "value": row['value'],
            "unit": row['unit'],
            'datetime': row['datetime'],
            'container_name': container_name,
        })
    for ano in anomalie["anomaly"] :
        anomaly_without_id.append({
            "topic": ano['topic'],
            "value": ano['value'],
            "unit": ano['unit'],
            'datetime': ano['datetime'],
            'container_name': container_name
        })
    new_anomaly = {'objects': []}
    data = mongo_client.find({ "container_name": container_name })
    if data_histor.count() != 0:
        for ano in anomaly_without_id :
            data = mongo_client.find({ "container_name": container_name })
            for row in data:
                if ano in data_without_id['objects'] :
                    if ano['datetime'] == row['datetime'] and ano['topic'] == row ['topic'] and ano['unit'] == row ['unit'] and ano['container_name'] == row ['container_name'] :
                        mongo_client.update_one({"_id":row ['_id']},{"$set":{"endDate_detection": datetime.datetime.strptime(str(new_date), "%Y-%m-%dT%H:%M:%S.%fZ")}})
                else :
                    for ano_add in anomalie["anomaly"] :
                        if ano_add not in new_anomaly['objects'] :
                            if ano['datetime'] == ano_add['datetime'] and ano['topic'] == ano_add ['topic'] and ano['unit'] == ano_add ['unit'] :
                                new_anomaly['objects'].append({
                                    "topic": ano_add['topic'],
                                    "value": ano_add['value'],
                                    "unit": ano_add['unit'],
                                    'datetime': ano_add['datetime'],
                                    'endDate_detection': ano_add['endDate_detection'],
                                    'startDate_detection': ano_add['startDate_detection'],
                                    'container_name': container_name
                                })

        for ano in new_anomaly['objects'] :
            mongo_client.insert_one(ano)
    else :
        for ano in anomalie["anomaly"] :
            mongo_client.insert_one(ano)
    return None


sys.modules[__name__] = insert_anomaly