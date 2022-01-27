from flask import current_app
from pymongo import MongoClient
from bson.objectid import ObjectId
import swiftclient
from swiftclient.service import SwiftService
import datetime
from bson.json_util import dumps
from datetime import datetime as dt
from time import sleep



def get_swift_original_object_name(swift_container_name, swift_object_id):
    """
    get swift original object name by object id
    :param swift_container_name:
    :param swift_object_id:
    :return: swift original object/file name
    """
    mongodb_url = current_app.config['MONGO_URL']
    mongo_client = MongoClient(mongodb_url, connect=False)
    mongo_db = mongo_client.swift
    mongo_collection = mongo_db[swift_container_name]
    metadata_swift = mongo_collection.find_one(
        {"swift_object_id": swift_object_id})

    return metadata_swift.get('original_object_name')

def get_last_metadata(db_name, params):
    mongodb_url = current_app.config['MONGO_URL']
    mongo_client = MongoClient(mongodb_url, connect=False)
    mongo_db = mongo_client.swift
    collection = mongo_db[db_name]

    metadata = collection.find()

    # Sort columns
    if("sort_field" in params.keys() and "sort_value" in params.keys()):
        metadata.sort(params['sort_field'], params['sort_value'])
    else:
        metadata.sort("creation_date", -1)
        
    if("offset" in params.keys() and "limit" in params.keys()):
        metadata = metadata.skip(params['offset'])
        metadata = metadata.limit(params['limit'])

    nb_objects = metadata.count()

    return nb_objects, metadata


def get_metadata(db_name, params):
    mongodb_url = current_app.config['MONGO_URL']
    mongo_client = MongoClient(mongodb_url, connect=False)
    mongo_db = mongo_client.swift
    collection = mongo_db[db_name]

    start_date = params['beginDate']
    end_date = params['endDate']

    metadata = collection.find(
        {'creation_date': {'$exists': 'true', '$ne': []}})
    dict_query = {"$and": []}

    if(params['filetype'] != ""):
        filetype_query = {"content_type": {'$in': params['filetype']}}
        dict_query['$and'].append(filetype_query)

    if(params['beginDate'] != "" and params['endDate'] != ""):
        dates_query = {'creation_date': {'$gte': start_date, '$lt': end_date}}
        for item in [dates_query]:
            dict_query['$and'].append(item)

    metadata = collection.find(dict_query)

    # Sort columns
    if("sort_field" in params.keys() and "sort_value" in params.keys()):
        metadata.sort(params['sort_field'], params['sort_value'])
    else:
        metadata.sort("creation_date", -1)

    if("offset" in params.keys() and "limit" in params.keys()):
        metadata = metadata.skip(params['offset'])
        metadata = metadata.limit(params['limit'])

    nb_objects = metadata.count() 

    return nb_objects, metadata


def get_id():
    mongodb_url = current_app.config['MONGO_URL']
    mongo_client = MongoClient(mongodb_url)
    return mongo_client.stats.swift.find_one_and_update({"type": "object_id_file"}, {"$inc": {"object_id": 1}})[
        "object_id"]


def init_id():
    id_doc = {"type": "object_id_file", "object_id": 0}
    mongodb_url = current_app.config['MONGO_URL']
    client = MongoClient(mongodb_url).stats.swift
    if MongoClient(mongodb_url).stats.swift.find_one(
            {"type": "object_id_file"}) is None:
        client.insert_one(id_doc)
    client.create_index("type", unique=True)


def insert_datalake(file_content, user, key, authurl, container_name,
                    file_name, processed_data_area_service, data_process,
                    application, content_type,
                    mongodb_url, other_data):
    conn = swiftclient.Connection(user=user, key=key,
                                  authurl=authurl)
    client = MongoClient(mongodb_url, connect=False)
    db = client.swift
    coll = db[container_name]
    if content_type is not None:
        # TODO : Check MIME type
        pass
    meta_data = {}
    if content_type is not None:
        meta_data["content_type"] = content_type
    else:
        meta_data["content_type"] = "None"
    meta_data["data_processing"] = data_process
    meta_data["swift_user"] = user
    meta_data["swift_container"] = container_name
    meta_data["swift_object_id"] = str(get_id()+1)
    if application is not None:
        meta_data["application"] = application
    else:
        meta_data["application"] = user + "_" + container_name
    meta_data["original_object_name"] = file_name
    meta_data["creation_date"] = datetime.datetime.now()
    meta_data["last_modified"] = datetime.datetime.now()
    meta_data["successful_operations"] = []
    meta_data["failed_operations"] = []
    meta_data["processed_data_area_service"] = processed_data_area_service
    if meta_data is not None:
        meta_data["other_data"] = other_data
    else:
        meta_data["other_data"] = {}
    _opts = {}
    stats_it = SwiftService(_opts).stat(
        container=container_name, objects=None, options=None)
    if stats_it["object"] is None:
        conn.put_container(container_name)
    retry = 0
    while True:
        try:
            conn.put_object(container_name, meta_data["swift_object_id"],
                            contents=file_content,
                            content_type=meta_data["content_type"])
            coll.insert_one(meta_data)
            return None
        except Exception as e:
            print(e)
            retry += 1
            if retry > 3:
                return None


def get_handled_data(params):
    mongodb_url = current_app.config['MONGO_URL']
    mongo_client = MongoClient(mongodb_url)

    mongo_database = ""
    collection_name = ""

    start = dt.strptime(params.get('beginDate'), '%Y-%m-%d')
    end = dt.strptime(params.get('endDate'), '%Y-%m-%d')

    # if certain filetype is selected, query will be ran on different MongoDB database
    # Example : Image -> data_conso database
    if("metadata" in params.get('dataType')):
        # Database "data_historique"
        mongo_database = mongo_client.data_conso

        # Collection "traitement_historique"
        collection_name = "processed_data"

        start = start.isoformat()
        end = end.isoformat()

        # Collection "traitement_historique"
        collection_traitement_historique = mongo_database[collection_name]

        # Query result (Cursor object)
        result_query = collection_traitement_historique.find(
            {'creation_date': {'$gte': start, '$lt': end}}, {"content_image": False})

    if(collection_name == ""):
        return {}, 0

    # Conversion to a list of dictionaries
    list_cursor = list(result_query)

    # JSON Conversion
    json_result = dumps(list_cursor)
    count = result_query.count()

    return json_result, count


def get_models_all():
    """
    get models with status true
    :return: all models
    """
    mongodb_url = current_app.config['MONGO_URL']
    mongo_client = MongoClient(mongodb_url, connect=False)
    mongo_db = mongo_client.models_management
    models = mongo_db["models"]
    metadata_models = models.find()
    return metadata_models

def get_models_show_all():
    """
    get models with status true
    :return: all models
    """
    mongodb_url = current_app.config['MONGO_URL']
    mongo_client = MongoClient(mongodb_url, connect=False)
    mongo_db = mongo_client.models_management
    models = mongo_db["models"]
    metadata_models = models.find({"status": True})
    return metadata_models

def get_models_all_cache():
    """
    get models with status false
    :return: all models
    """
    mongodb_url = current_app.config['MONGO_URL']
    mongo_client = MongoClient(mongodb_url, connect=False)
    mongo_db = mongo_client.models_management
    models = mongo_db["models"]
    metadata_models = models.find({"status": False})
    return metadata_models

def get_model_id(id):
    """
    get model with id
    :param id
    :return: a model
    """
    mongodb_url = current_app.config['MONGO_URL']
    mongo_client = MongoClient(mongodb_url, connect=False)
    mongo_db = mongo_client.models_management
    models = mongo_db["models"]
    query = {"_id": ObjectId(id)}
    metadata_models_param = models.find(query)

    return metadata_models_param

def get_models_params(param):
    """
    get models with param string
    :param 
    :return: all models
    """
    mongodb_url = current_app.config['MONGO_URL']
    mongo_client = MongoClient(mongodb_url, connect=False)
    mongo_db = mongo_client.models_management
    models = mongo_db["models"]
    query = {"type_file_accepted": param, "status": True}
    metadata_models_param = models.find(query)

    return metadata_models_param


def add_model(param):
    """
    insert model
    :param 
    :return: done
    """
    mongodb_url = current_app.config['MONGO_URL']
    mongo_client = MongoClient(mongodb_url, connect=False)
    mongo_db = mongo_client.models_management
    models = mongo_db["models"]
    models.insert_one(param)
    result = "done"
    return result


def update_model(param):
    """
    update model
    :param 
    :return: done
    """
    mongodb_url = current_app.config['MONGO_URL']
    mongo_client = MongoClient(mongodb_url, connect=False)
    mongo_db = mongo_client.models_management
    models = mongo_db["models"]
    query = {"_id": ObjectId(param['id'])}
    updatevalues = {"$set": {
        "label": param['label'],
        "type_file_accepted": param['type_file_accepted'],
        "metadonnees": param['metadonnees'],
        "status": param['status']
    }}
    
    models.update_one(query, updatevalues, upsert=False)
    result = "done"
    return result


def insert_anomaly(anomaly,endDate):
    """
    insert_anomaly from influx db to mongodb 
    :param anomaly:
    :param endDate:
    :return: done
    """
    mongodb_url = current_app.config['MONGO_URL']
    anomalie = anomaly
    mongo_client = MongoClient(mongodb_url).data_anomaly.influxdb_anomaly
    data_histor = mongo_client.find()
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
            'datetime': row['datetime']
        })
    for ano in anomalie["anomaly"] :
        anomaly_without_id.append({
            "topic": ano['topic'],
            "value": ano['value'],
            "unit": ano['unit'],
            'datetime': ano['datetime']
        })
    new_anomaly = {'objects': []}
    data = mongo_client.find()
    if data_histor.count() != 0:
        for ano in anomaly_without_id :
            data = mongo_client.find()
            for row in data:
                if ano in data_without_id['objects'] :
                    if ano['datetime'] == row['datetime'] and ano['topic'] == row ['topic'] and ano['unit'] == row ['unit'] :
                        print("update ici ")
                        mongo_client.update_one({"_id":row ['_id']},{"$set":{"endDate_detection": datetime.datetime.strptime(str(new_date), "%Y-%m-%dT%H:%M:%S.%fZ")}})
                else :
                    for ano_add in anomalie["anomaly"] :
                        if ano_add not in new_anomaly['objects'] :
                            if ano['datetime'] == ano_add['datetime'] and ano['topic'] == ano_add ['topic'] and ano['unit'] == ano_add ['unit'] :
                                print("insert ici ")
                                new_anomaly['objects'].append({
                                    "topic": ano_add['topic'],
                                    "value": ano_add['value'],
                                    "unit": ano_add['unit'],
                                    'datetime': ano_add['datetime'],
                                    'endDate_detection': ano_add['endDate_detection'],
                                    'startDate_detection': ano_add['startDate_detection']
                                })

        for ano in new_anomaly['objects'] :
            print("new anomaly ")
            mongo_client.insert_one(ano)  
    else :
        for ano in anomalie["anomaly"] :
            mongo_client.insert_one(ano)            
    result = "done"
    return result


def get_anomaly(params,measurement,topic):
    """
    get_anomaly from 
    :param params: start date & end date 
    :param measurement:
    :param topic: 
    :return: metadate
    """
    mongodb_url = current_app.config['MONGO_URL']
    collection = MongoClient(mongodb_url, connect=False).data_anomaly.influxdb_anomaly

    start_date =  datetime.datetime.strptime(str(params['beginDate']), "%Y-%m-%dT%H:%M:%S.%fZ")
    end_date = datetime.datetime.strptime(str(params['endDate']), "%Y-%m-%dT%H:%M:%S.%fZ")
    topic = topic
    measurement = measurement
    dict_query = {"$and": []}
    if(start_date != "" and end_date != "" and topic != "" and measurement != ""):
        dates_query = {'unit': measurement}
        for item in [dates_query]:
            dict_query['$and'].append(item)

        dates_query = {'topic': topic}
        for item in [dates_query]:
            dict_query['$and'].append(item)

        dates_query = {'startDate_detection': {'$gte': start_date}}
        for item in [dates_query]:
            dict_query['$and'].append(item)

        dates_query = {'endDate_detection': {'$lt': end_date}}
        for item in [dates_query]:
            dict_query['$and'].append(item)

    metadata = collection.find(dict_query)
    #print(metadata)
    return metadata


def get_anomaly_all():
    """
    get all anomaly from mongodb

    :return: metadate
    """
    mongodb_url = current_app.config['MONGO_URL']
    collection = MongoClient(mongodb_url, connect=False).data_anomaly.influxdb_anomaly

    metadata = collection.find()
    nbr_metadata = metadata.count()
    return nbr_metadata, metadata