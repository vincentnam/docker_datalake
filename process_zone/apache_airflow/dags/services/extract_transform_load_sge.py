import sys
import config
from io import StringIO
import tempfile
from pymongo import MongoClient
import config
from services import restore_backup
from services import restore_diff

# Handling function about SQL dumps
def extract_transform_load_sge(swift_result, swift_container, swift_id, process_type):
    
    #Connection mongodb
    mongo_client = MongoClient(config.mongodb_url, username=config.mongodb_user, password=config.mongodb_pwd, authSource=config.mongodb_db_auth)
    db = mongo_client.swift[config.container_name_collection_upload]
    result = db.find_one({"swift_object_id": swift_id}, {"_id" : 0})
    filename = result["original_object_name"]

    filename_split = filename.split("_")
    last_filename_split = filename_split[len(filename_split) - 1]
    if( last_filename_split == "Differentielle"):
        print("Diff")
        restore_diff(swift_result, filename_split[0])
    else:
        print("Dump")
        restore_backup(swift_result, filename)
    
    return [{'result': 'Insert done'}]

sys.modules[__name__] = extract_transform_load_sge