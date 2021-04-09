from pymongo import MongoClient
import swiftclient
import datetime
import yaml

# get connection config
with open("./config.yml", "r") as config:
    conf = yaml.safe_load(config)

swift_container_name = "test_neocampus"

# a csv file for test
test_file_name = "test.csv"
test_file_path = "./data/" + test_file_name
with open(test_file_path, "rb") as f:
    file_content = f.read()

# the following values are just for test
meta_data = {
    'file_name': test_file_name,
    "content_type": "text/csv",
    "process_time": datetime.datetime.now(),
    "swift_user": conf.get('SWIFT_USER'),
    "swift_container": swift_container_name,
    "swift_object_id": f"test_obj_{round(datetime.datetime.now().timestamp())}",
}

# swift connection
swift_authurl = "http://" + conf.get('OPENSTACK_SWIFT_IP') + ":" + conf.get('SWIFT_REST_API_PORT') + "/auth/v1.0"
swift_conn = swiftclient.Connection(user=conf.get("SWIFT_USER"), key=conf.get("SWIFT_KEY"), authurl=swift_authurl)

# mongodb connection
mongodb_url = conf.get('META_MONGO_IP') + ":" + conf.get('MONGO_PORT')
mongo_client = MongoClient(mongodb_url, connect=False)
mongo_db = mongo_client.swift

mongo_collection = mongo_db[swift_container_name]

try:
    # create swift container
    swift_conn.put_container(swift_container_name)
    # upload object
    swift_result = swift_conn.put_object(swift_container_name,
                                         meta_data["swift_object_id"],
                                         contents=file_content,
                                         content_type=meta_data["content_type"])

    print(swift_result)
    # insert data in mongodb
    mongo_result = mongo_collection.insert_one(meta_data)
    print(mongo_result)
except Exception as e:
    print(e)
