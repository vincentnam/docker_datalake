import sys
from datetime import datetime
import datetime
from textwrap import dedent
from pymongo import MongoClient
import json
from bson import ObjectId
from json import JSONEncoder
import get_metadata
import config

# Fonction de traitement d'une image
def extract_transform_load_images(swift_result, swift_container, swift_id, process_type):
    print(swift_id)
    str_swift_id = str(swift_id)
    print(str_swift_id)
    
    # Décodage de l'image
    image = str(swift_result,'utf-8')
    #URL Mongo
    mongodb_url = config.mongodb_url
    container_name_collection_upload = config.container_name_collection_upload
    #Recuperation de la collection mongo avec en paramètre le swift_id
    nb_objects, mongo_collections = get_metadata(container_name_collection_upload, mongodb_url ,{"swift_id": str_swift_id})
    mongo_collections = list(mongo_collections)
    
    #Recupération des autres métadata
    other_metadata = []
    for obj in mongo_collections:
        other_metadata.append(obj['other_data'])
    
    #Configuration de mongo pour le processed data 
    container_name = config.container_name_processed_data
    client = MongoClient(mongodb_url, connect=False)
    db = client.data_conso
    collection = db[container_name]
    
    #Configuration de l'object data_conso_image pour l'inserer dans mongo
    data_conso_image = {}

    data_conso_image["swift_id"] = str_swift_id
    data_conso_image["content_image"] = image
    data_conso_image["image_metadata"] = other_metadata
    data_conso_image["creation_date"] = datetime.datetime.now()
    
    # Encode DateTime and ObjectId Object into JSON using custom JSONEncoder
    data_conso_image = JSONEncoder().encode(data_conso_image)
    # Decode data_conso_image
    data_conso_image = json.loads(data_conso_image)
    #Insertion dans mongo
    collection.insert_one(data_conso_image)
    #Encode data_conso_image pour afficher dans le dag le resultat
    data_conso_image = JSONEncoder().encode(data_conso_image)
    return data_conso_image

#Class pour l'encodage du Json
class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, (ObjectId)):
            return str(o)
        if isinstance(o, (datetime.datetime)):
            return o.isoformat()
        return json.JSONEncoder.default(self, o)


sys.modules[__name__] = extract_transform_load_images
