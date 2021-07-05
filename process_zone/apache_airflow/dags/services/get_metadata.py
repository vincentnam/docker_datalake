import sys
from pymongo import MongoClient

#Fonction de recherche dans la collection avec comme paramètre l'id swift
def get_metadata(db_name, mongodb_url, params):
    mongo_client = MongoClient(mongodb_url, connect=False)
    mongo_db = mongo_client.swift
    collection = mongo_db[db_name]

    metadata = collection.find({ 'creation_date': { '$exists': 'true', '$ne': [] } })
    dict_query = {"$and": []}

    if(params['swift_id'] != ""):
        datatype_query = {"swift_object_id": params['swift_id']}
        for item in [datatype_query]: 
            dict_query['$and'].append(item)

    metadata = collection.find(dict_query)

    nb_objects = metadata.count()

    return nb_objects, metadata


sys.modules[__name__] = get_metadata
