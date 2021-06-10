from pymongo import MongoClient
import swiftclient.service
from swiftclient.service import SwiftService

swift_id = "201"

def get_id():
    mongodb_url = "URL_MONGO"
    mongo_client = MongoClient(mongodb_url)
    return mongo_client.stats.swift.find_one_and_update({"type": "object_id_file"}, {"$inc": {"object_id": 1}})[
            "object_id"]


def get_metadata(db_name, params):
    mongodb_url = "url_mongo"
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
    
swift_id = get_id()+1
str_swift_id = str(swift_id)

authurl = "http://url/auth/v1.0"
user = 'test:tester'
key = 'testing'
conn = swiftclient.Connection(
    user=user, 
    key=key,
    authurl=authurl
)
swift_object = conn.get_object(swift_container, swift_id)
print('----------- OBJET SWIFT -------------')
print(swift_object)

content_type = swift_object[0]['content-type']
swift_result = swift_object[1]
s = str(swift_result,'utf-8')

nb_objects, metadata = get_metadata("neOCampus", {"swift_id": str_swift_id})




