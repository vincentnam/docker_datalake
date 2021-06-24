import sys
from pymongo import MongoClient
from datetime import datetime

def history_data(
    process_type, 
    swift_container, 
    swift_object_id, 
    task_type,
    mongo_column,
    old_data,
    new_data
):
    meta_data = {} 

    meta_data["creation_date"] = datetime.now()
    meta_data['swift_container'] = swift_container
    meta_data['swift_id'] = swift_object_id
    meta_data['process_type'] = process_type
    meta_data['task_type'] = task_type
    meta_data['old_data'] = old_data
    meta_data['new_data'] = new_data

    # Metadata
    mongo_column.insert_one(meta_data)
    

sys.modules[__name__] = history_data
