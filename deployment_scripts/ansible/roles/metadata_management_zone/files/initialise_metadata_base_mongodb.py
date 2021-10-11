from pymongo import MongoClient
import sys

# First argument is mongodb_url
# IP_ADDR:PORT
mongodb_url = sys.argv[1]
id_doc = {"type": "object_id_file", "object_id": 0}
client = MongoClient(mongodb_url).stats.swift
if MongoClient(mongodb_url).stats.swift.find_one(
        {"type": "object_id_file"}) is None:
    client.insert_one(id_doc)
client.create_index("type", unique=True)
