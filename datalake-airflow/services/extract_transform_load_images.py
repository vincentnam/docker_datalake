import sys
from datetime import datetime
import datetime
from textwrap import dedent
from pymongo import MongoClient
import json
from bson import ObjectId
from json import JSONEncoder
import get_metadata


def extract_transform_load_images(swift_result, swift_container, swift_id, coll, process_type, mongodb_url):
    # TODO : process related to images
    
    print(swift_id)
    str_swift_id = str(swift_id)
    print(str_swift_id)
    
    image = str(swift_result,'utf-8')
    
    nb_objects, mongo_collections = get_metadata("neOCampus", mongodb_url ,{"swift_id": str_swift_id})
    mongo_collections = list(mongo_collections)
    
    other_metadata = []
    for obj in mongo_collections:
        other_metadata.append(obj['other_data'])
    
    container_name = "processed_data"
    client = MongoClient(mongodb_url, connect=False)
    db = client.data_conso
    collection = db[container_name]
    
    data_conso_image = {}

    data_conso_image["swift_id"] = str_swift_id
    data_conso_image["content_image"] = image
    data_conso_image["image_metadata"] = other_metadata
    data_conso_image["creation_date"] = datetime.datetime.now()
    
    # Encode DateTime and ObjectId Object into JSON using custom JSONEncoder
    data_conso_image = JSONEncoder().encode(data_conso_image)
    print(type(data_conso_image))
    data_conso_image = json.loads(data_conso_image)

    collection.insert_one(data_conso_image)
    data_conso_image = JSONEncoder().encode(data_conso_image)
    return data_conso_image

class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, (ObjectId)):
            return str(o)
        if isinstance(o, (datetime.datetime)):
            return o.isoformat()
        return json.JSONEncoder.default(self, o)


sys.modules[__name__] = extract_transform_load_images
