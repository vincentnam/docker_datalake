from pymongo import MongoClient

import swiftclient.service
from swiftclient.service import SwiftService
import datetime

import swiftclient.service


def get_id(mongodb_url):
    mongo_forid_co = MongoClient(mongodb_url)
    return mongo_forid_co.stats.swift.find_one({"type": "object_id_file"})[
        "object_id"]


def init_id():
    # USE IT ONLY ONE TIME !!
    id_doc = {"type": "object_id_file", "object_id": 0}
    client = MongoClient("127.0.0.1:27017").stats.swift
    if MongoClient("127.0.0.1:27017").stats.swift.find_one(
            {"type": "object_id_file"}) is None:
        client.insert_one(id_doc)
    client.create_index("type", unique=True)


def clean_swift(container):
    pass


def insert_datalake(file_content, user, key, authurl, container_name,
                    file_name=None, application=None, content_type=None,
                    mongodb_url="127.0.0.1:27017"):
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

    '''
    conn = swiftclient.Connection(user=user, key=key,
                                  authurl=authurl)
    client = MongoClient(mongodb_url)
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
    meta_data["swift_user"] = user
    meta_data["swift_container"] = container_name
    meta_data["swift_object_id"] = str(get_id(mongodb_url))
    if application is not None:
        meta_data["application"] = application
    else:
        meta_data["application"] = user + "_" + container_name
    if file_name is not None:
        meta_data["swift_object_name"] = file_name
    meta_data["creation_date"] = datetime.datetime.now()
    meta_data["last_modified"] = datetime.datetime.now()
    meta_data["successful_operations"] = []
    meta_data["failed_operations"] = []
    print(meta_data)

    if SwiftService({}).stat(container_name)["object"] is None:
        conn.put_container(container_name)
    # Gérer l'atomicité de cette partie #

    coll.insert_one(meta_data)
    retry = 0
    while True:
        try:
            conn.put_object(container_name, meta_data["swift_object_id"],
                            contents=file_content,
                            content_type=meta_data["content_type"])#,
                            # headers={"x-webhook":"yes"})

            client.stats.swift.update_one({"type": "data_to_process_list"},
                                          {"$push":
                                              {
                                                  "data_to_process": {
                                                      "swift_id": meta_data[
                                                          "swift_object_id"],
                                                      "swift_container":
                                                          meta_data[
                                                              "swift_container"],
                                                      "swift_user": meta_data[
                                                          "swift_user"],
                                                      "content_type":
                                                          meta_data[
                                                              "content_type"]
                                                  }
                                              }
                                          }
                                          )

            client.stats.swift.update_one({"type": "object_id_file"},
                                          {"$inc": {"object_id": 1}})
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


# TODO: Finir le JSON des fichiers

# TODO : Voire pour la segmentation d'image (https://github.com/facebookresearch/Detectron2)


user = 'test:tester'
key = 'testing'

client = MongoClient("127.0.0.1:27017")
# init_id()


authurl = "http://127.0.0.1:8080/auth/v1.0"
conn = swiftclient.Connection(user=user, key=key,
                              authurl=authurl)
file_name = "Openstack/swift/input_file_test/log.json"

with open(file_name, "rb") as f:
    file_data = f.read()

file_content = open(file_name, "r")
print(file_data)
container_name = "neocampus"

insert_datalake(file_data, user, key, authurl, container_name,
                application="neocampus sensors log",
                content_type="application/json", mongodb_url="127.0.0.1:27017")

# input_csv_file("./dataset/mygates/subset.csv", sep=";", header=0, projet="mygates",authurl = "http://127.0.0.1:12345/auth/v1.0",container_name = "mygates")

# swift stat -U test:tester -A http://localhost:8080/auth/v1.0 -K testing CONTAINER

# sshfs vdang@co2-dl-airflow:/projets/datalake/airflow/ /data/python-project/docker_datalake/mnt_temp
# TODO : Reinstaller Openstack Swift avec Python3
#

