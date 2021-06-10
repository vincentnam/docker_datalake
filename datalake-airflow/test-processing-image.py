from pymongo import MongoClient
import swiftclient.service
from swiftclient.service import SwiftService

swift_id = "201"

def get_id():
    mongodb_url = "URL_MONGO"
    mongo_client = MongoClient(mongodb_url)
    return mongo_client.stats.swift.find_one_and_update({"type": "object_id_file"}, {"$inc": {"object_id": 1}})[
            "object_id"]
    
swift_id = get_id()+1



