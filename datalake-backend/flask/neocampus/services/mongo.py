from flask import current_app
from pymongo import MongoClient


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
    print(params['offset'])
    print(params['limit'])
    mongodb_url = current_app.config['MONGO_URL']
    mongo_client = MongoClient(mongodb_url, connect=False)
    mongo_db = mongo_client.swift
    collection = mongo_db[db_name]

    metadata = collection.find()

    nb_objects = collection.find().count()

    if(params['filetype']):
        print('filetype')
        metadata = collection.find({"content_type": params['filetype']})

    if(params['offset']):
        print('offset')
        metadata = metadata.skip(params['offset'])

    if(params['limit']):
        print('limit')
        metadata = metadata.limit(params['limit'])

    return nb_objects, metadata
