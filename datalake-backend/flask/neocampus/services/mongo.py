from flask import current_app
from pymongo import MongoClient
from datetime import datetime


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
    metadata_swift = mongo_collection.find_one({"swift_object_id": swift_object_id})

    return metadata_swift.get('original_object_name')


def get_metadata(db_name, params):
    mongodb_url = current_app.config['MONGO_URL']
    mongo_client = MongoClient(mongodb_url, connect=False)
    mongo_db = mongo_client.swift
    collection = mongo_db[db_name]

    start_date = params['beginDate']
    end_date = params['endDate']

    metadata = collection.find({ 'creation_date': { '$exists': 'true', '$ne': [] } })
    dict_query = {"$and": []}

    if(params['filetype'] != ""):
        filetype_query = {"content_type": params['filetype']}
        for item in [filetype_query]: 
            dict_query['$and'].append(item) 

    if(params['beginDate'] != "" and params['endDate'] != ""):
        dates_query = {'creation_date': {'$gte': start_date, '$lt': end_date}}
        for item in [dates_query]: 
            dict_query['$and'].append(item) 

    if(params['datatype'] != ""):
        datatype_query = {"swift_container": params['datatype']}
        for item in [datatype_query]: 
            dict_query['$and'].append(item)

    metadata = collection.find(
        {"$and": [
            {'creation_date': {'$gte': start_date, '$lt': end_date}},
            {"content_type": params['filetype']}
        ]}
    )

    if(params['offset']):
        metadata = metadata.skip(params['offset'])

    if(params['limit']):
        metadata = metadata.limit(params['limit'])

    

    nb_objects = metadata.count()

    return nb_objects, metadata
