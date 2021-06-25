import sys
from pymongo import MongoClient
from datetime import datetime
import config

# Fonction d'historisation
def history_data(
    process_type, 
    swift_container, 
    swift_object_id, 
    task_type,
    old_data,
    new_data
):
    mongodb_url = config.mongodb_url
    container_name = config.container_name

    # Configuration de mongo for Historique
    client = MongoClient(mongodb_url, connect=False)
    db = client.data_historique
    coll = db[container_name]
    
    #Configuration de l'objet d'historisation: history_data
    history_data = {} 

    history_data["creation_date"] = datetime.now()
    history_data['swift_container'] = swift_container
    history_data['swift_id'] = swift_object_id
    history_data['process_type'] = process_type
    history_data['task_type'] = task_type
    history_data['old_data'] = old_data
    history_data['new_data'] = new_data

    # Insertion de l'object d'historisation dans mongo
    coll.insert_one(history_data)
    

sys.modules[__name__] = history_data
