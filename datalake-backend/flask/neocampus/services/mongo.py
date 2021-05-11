import datetime
from flask import current_app
from pymongo import MongoClient
import swiftclient
from swiftclient.service import SwiftService



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

<<<<<<< HEAD
    return nb_objects, collections


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
    stats_it = SwiftService(_opts).stat(container=container_name, objects=None, options=None)
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
=======
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
>>>>>>> 36f4f0d... change route method and added parameters
