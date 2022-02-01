import sys
from pymongo import MongoClient
import config

# Function return metadata from a swift_object_id
def connection_mongo_metadata(swift_container, swift_object_id):
    mongodb_url = config.mongodb_url
    container_name = swift_container

    # Connection to mongodb metadata
    client = MongoClient(mongodb_url, connect=False)
    db = client.swift
    coll = db[container_name]
    # Find data with the swift_object_id
    metadata_doc = coll.find({'swift_object_id': swift_object_id}, {'_id': 0})

    return metadata_doc[0]
    

sys.modules[__name__] = connection_mongo_metadata
