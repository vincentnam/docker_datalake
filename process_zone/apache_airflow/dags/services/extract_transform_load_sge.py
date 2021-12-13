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

    # Start of treatment 
    # A tester 
    # data=str(swift_result,'utf-8').replace("\\n", "\n")
    # lines = StringIO()
    # lines.write(s)
    # lines.seek(0)
    # data = []
    # for line in lines:
    #     line = line.replace("\n","")
    #     data.append(line)
    
    mongo_client = MongoClient(config.mongodb_url)
    db = mongo_client.swift[config.container_name_collection_upload]
    result = db.find_one({"swift_object_id": swift_id}, {"_id" : 0})
    filename = result["original_object_name"]

    filename_split = filename.split("_")
    if(filename_split[1] == "Différentielle"):
        print("Diff")
        restore_diff(swift_result, filename_split[1])
    else:
        print("Dump")
        restore_backup(swift_result, filename_split[1])
    
    return [{'result': 'Insert done'}]

sys.modules[__name__] = extract_transform_load_sge