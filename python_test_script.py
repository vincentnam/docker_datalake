from pymongo import MongoClient

import swiftclient.service
from swiftclient.service import SwiftService
import datetime

import swiftclient.service


def get_id(mongodb_url):
    mongo_forid_co = MongoClient(mongodb_url)
    return mongo_forid_co.stats.swift.find_one_and_update({"type": "object_id_file"},   {"$inc": {"object_id": 1}})[
        "object_id"]


def init_id(mongo_url):
    # USE IT ONLY ONE TIME !!
    id_doc = {"type": "object_id_file", "object_id": 0}
    client = MongoClient(mongo_url).stats.swift
    if MongoClient(mongo_url).stats.swift.find_one(
            {"type": "object_id_file"}) is None:
        client.insert_one(id_doc)
    client.create_index("type", unique=True)


def clean_swift(container):
    pass


def insert_datalake(file_content, user, key, authurl, container_name,
                    file_name, data_process = "default", application=None, content_type=None,
                    mongodb_url="127.0.0.1:27017", other_data = None ):
    '''
    Insert data in the datalake :
        - In Openstack Swift for data
        - In MongoDB for metadata

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
    if meta_data is not None :
        meta_data["other_data"] = other_data
    else:
        meta_data["other_data"] ={}
    print(meta_data)

    if SwiftService({}).stat(container_name)["object"] is None:
        conn.put_container(container_name)
    # Gérer l'atomicité de cette partie #

    retry = 0
    while True:
        try:
            conn.put_object(container_name, meta_data["swift_object_id"],
                            contents=file_content,
                            content_type=meta_data["content_type"])#,
            # headers={"x-webhook":"yes"})
            # Insert metadata over the data : only if data has been put
            coll.insert_one(meta_data)
            # client.stats.swift.update_one({"type": "data_to_process_list"},
            #                               {"$push":
            #                                   {
            #                                       "data_to_process": {
            #                                           "swift_id": meta_data[
            #                                               "swift_object_id"],
            #                                           "swift_container":
            #                                               meta_data[
            #                                                   "swift_container"],
            #                                           "swift_user": meta_data[
            #                                               "swift_user"],
            #                                           "content_type":
            #                                               meta_data[
            #                                                   "content_type"]
            #                                       }
            #                                   }
            #                               }
            #                               )
            return None
        except Exception as e:
            print(e)
            retry += 1
            if retry > 3:
                return None


#####################################
import pandas as pd
import os
import mimetypes


def input_csv_file(csv_file, **kwargs):
    df = pd.read_csv(csv_file, sep=kwargs["sep"], header=kwargs["header"])
    print(df.keys())
    for i in df.iloc:
        meta_data = {
            "content_type": mimetypes.guess_type(i["file_name"])[0],
            "projet": kwargs["projet"],
        }

        print(type(i["main_object"]))
        for j in i.keys():
            meta_data[j] = str(i[j])
        print(meta_data)
        with open(os.path.join(meta_data["path"], meta_data["file_name"]),
                  "rb") as f:
            file_data = f.read()
        insert_datalake(file_data, user, key, kwargs["authurl"],
                        kwargs["container_name"],
                        mongodb_url="127.0.0.1:27017")
        break

# import os
#
# cwd = os.path.dirname(os.path.abspath(__file__))
# import yaml
# import json
# with open(cwd + "/apache_airflow/dags/config.yml", "r") as config:
#     y = yaml.safe_load(config)
# globals().update(y)
# # TODO: Finir le JSON des fichiers
#
# # TODO : Voire pour la segmentation d'image (https://github.com/facebookresearch/Detectron2)
#
#
# user = 'test:tester'
# key = 'testing'
# mongo_url = globals()["META_MONGO_IP"] + ":" + globals()["MONGO_PORT"]
# # mongo_url = "127.0.0.1:" + globals()["MONGO_PORT"]
# client = MongoClient(globals()["META_MONGO_IP"] + ":" + globals()["MONGO_PORT"])
# # init_id(mongo_url)
#
#
# authurl = "http://"+ globals()["OPENSTACK_SWIFT_IP"]+":"+globals()["SWIFT_REST_API_PORT"]+"/auth/v1.0"
# conn = swiftclient.Connection(user=user, key=key,
#                               authurl=authurl)
# path = "/home/vdang/PycharmProjects/docker_datalake/apache_airflow/dags/"
# file_name = "dag1.json"
#
# with open(path+file_name, "rb") as f:
#     file_data = f.read()
#
# file_content = open(path+file_name, "r")
# print(file_data)
# container_name = "neocampus"
#
# insert_datalake(file_data, user, key, authurl, container_name, data_process="custom",
#                 application="osirim test", file_name=file_name,
#                 content_type="bson", mongodb_url=mongo_url,#globals()["META_MONGO_IP"] + ":" + globals()["MONGO_PORT"],
#                 other_data=
#                 {
#                     "template":
#                         {
#                             "measurement":"mesurevaleur",
#                             "time":"datemesure",
#                             "fields":["value"],
#                             "tags":["idpiece","idcapteur"]
#                         }
#                 }
#                 )
#
# # input_csv_file("./dataset/mygates/subset.csv", sep=";", header=0, projet="mygates",authurl = "http://127.0.0.1:12345/auth/v1.0",container_name = "mygates")
#
# # swift stat -U test:tester -A http://localhost:8080/auth/v1.0 -K testing CONTAINER
#
# # sshfs vdang@co2-dl-airflow:/projets/datalake/airflow/ /data/python-project/docker_datalake/mnt_temp
# # TODO : Reinstaller Openstack Swift avec Python3
# #

import os

cwd = os.path.dirname(os.path.abspath(__file__))
import yaml
import json
with open(cwd + "/apache_airflow/dags/config.yml", "r") as config:
    y = yaml.safe_load(config)
globals().update(y)
# TODO: Finir le JSON des fichiers

# TODO : Voire pour la segmentation d'image (https://github.com/facebookresearch/Detectron2)


user = 'test:tester'
key = 'testing'
mongo_url = globals()["META_MONGO_IP"] + ":" + globals()["MONGO_PORT"]
# mongo_url = "127.0.0.1:" + globals()["MONGO_PORT"]
client = MongoClient(globals()["META_MONGO_IP"] + ":" + globals()["MONGO_PORT"])
# init_id(mongo_url)


authurl = "http://"+ globals()["OPENSTACK_SWIFT_IP"]+":"+globals()["SWIFT_REST_API_PORT"]+"/auth/v1.0"
conn = swiftclient.Connection(user=user, key=key,
                              authurl=authurl)
path = "/home/vdang/Desktop/data/neocampus-mongodb_dump.mar20/"
file_name = "energy.bson"

with open(path+file_name, "rb") as f:
    file_data = f.read()

file_content = open(path+file_name, "r")
# print(file_data)
container_name = "neocampus"

insert_datalake(file_data, user, key, authurl, container_name, data_process="custom",
                application="import mongodb", file_name=file_name,
                content_type="bson", mongodb_url=mongo_url#globals()["META_MONGO_IP"] + ":" + globals()["MONGO_PORT"],
                )

# input_csv_file("./dataset/mygates/subset.csv", sep=";", header=0, projet="mygates",authurl = "http://127.0.0.1:12345/auth/v1.0",container_name = "mygates")

# swift stat -U test:tester -A http://localhost:8080/auth/v1.0 -K testing CONTAINER

# sshfs vdang@co2-dl-airflow:/projets/datalake/airflow/ /data/python-project/docker_datalake/mnt_temp
# TODO : Reinstaller Openstack Swift avec Python3
#
