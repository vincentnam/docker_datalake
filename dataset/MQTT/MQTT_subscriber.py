import paho.mqtt.client as mqtt
from pymongo import MongoClient
import swiftclient.service
from swiftclient.service import SwiftService
import datetime
import ast

def get_id(mongodb_url):
    mongo_forid_co = MongoClient(mongodb_url)
    return mongo_forid_co.stats.swift.find_one_and_update({"type": "object_id_file"},   {"$inc": {"object_id": 1}})[
        "object_id"]



def insert_datalake(file_content, user, key, authurl, container_name,
                    file_name, processed_data_area_service, data_process = "default",
                    application=None, content_type=None,
                    mongodb_url="127.0.0.1:27017",other_data = None ):
    '''
    Insert data in the datalake :
        - In Openstack Swift for data
        - In MongoDB for metadata

    :param processed_data_area_service: list of services in the processed data area in which to insert data
    :type processed_data_area_service : list[str]
    :param file_content: the data to insert :
        with open(file_name, "rb") as f:
            file_data = f.read()
    :type file_content : bytes
    :param user: user for Swift authentication
    :type user : str
    :param key: password for Swift authentication
    :type key : str
    :param authurl: URL for Swift authentication service, commonly :
        http://IP_ADDR:8080/auth/v1.0
    The IP_ADDR is the IP addresse where the service is installed
    (Openstack swift / Openstack keystone / ... ?)
    :type authurl : str
    :param container_name: name of the container on which write the data
    :type container_name: str
    :param file_name: the original file name
    :type file_name : str
    :param application: Description of the application where the data
    come from or whatever you want
    :type application : str
    :param content_type: MIME Type of the data
    :type content_type : str
    :param mongodb_url: the MongoDB IP_ADDR with Port
    :type mongodb_url : str
    :param data_process : process the data in default pipeline or custom one
    :type data_process : str : "default" or "custom"
    '''
    conn = swiftclient.Connection(user=user, key=key,
                                  authurl=authurl)
    client = MongoClient(mongodb_url, connect=False)
    db = client.swift
    coll = db[container_name]
    if content_type is not None:
        # TODO : Check MIME type
        pass
    meta_data = {}
    if content_type is not None:
        meta_data["content_type"] = content_type
    else:
        meta_data["content_type"] = "None"
    meta_data["data_processing"]= data_process
    meta_data["swift_user"] = user
    meta_data["swift_container"] = container_name
    meta_data["swift_object_id"] = str(get_id(mongodb_url))
    if application is not None:
        meta_data["application"] = application
    else:
        meta_data["application"] = user + "_" + container_name
    meta_data["original_object_name"] = file_name
    meta_data["creation_date"] = datetime.datetime.now()
    meta_data["last_modified"] = datetime.datetime.now()
    meta_data["successful_operations"] = []
    meta_data["failed_operations"] = []
    meta_data["processed_data_area_service"] = processed_data_area_service
    if meta_data is not None :
        meta_data["other_data"] = other_data
    else:
        meta_data["other_data"] ={}
    print(meta_data)

    if SwiftService({}).stat(container_name)["object"] is None:
        conn.put_container(container_name)
    # Gérer l'atomicité de cette partie #
#####################################################
    retry = 0
    while True:
        try:
            conn.put_object(container_name, meta_data["swift_object_id"],
                            contents=file_content,
                            content_type=meta_data["content_type"])
            coll.insert_one(meta_data)
            return None
        except Exception as e:
            print(e)
            retry += 1
            if retry > 3:
                return None
#####################################


# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.unsubscribe("$SYS/#")



# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))
    print(type(msg.payload))
    dict_str = msg.payload.decode("UTF-8")
    mydata = ast.literal_eval(dict_str)
    print(mydata)
    user = 'test:tester'
    key = 'testing'
    mongo_url = "141.115.103.31" + ":" + "27017"
    client = MongoClient("141.115.103.31" + ":" + "27017")

    time = str(datetime.datetime.now())

    mydata["time"] = time
    authurl = "http://" + "141.115.103.30" + ":" + "8080" + "/auth/v1.0"
    file_name = msg.topic + "_" + time
    container_name = "IDEAS_use_case"

    insert_datalake(str(mydata).encode(), user, key, authurl, container_name, processed_data_area_service=["InfluxDB"],
                    data_process="custom",  other_data={"flow_type":"stream"},
                    application="sensor reading", file_name=file_name,
                    content_type="application/json", mongodb_url=mongo_url)


client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message


user = ""
password = ""
URL = ""
PORT = 0
client.username_pw_set(username=user, password=password)

client.connect(URL, PORT , 60)
client.subscribe("u4/300/#")
# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.
client.loop_forever()

