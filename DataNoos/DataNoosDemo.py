from pymongo import MongoClient
import yaml
import swiftclient.service
from swiftclient.service import SwiftService
import datetime
import os
import swiftclient.service
import magic

cwd = os.path.dirname(os.path.abspath(__file__))
print(cwd)
with open(cwd + "/../apache_airflow/dags/config.yml", "r") as config:
    y = yaml.safe_load(config)
globals().update(y)


def get_id(mongodb_url):
    mongo_forid_co = MongoClient(mongodb_url)
    return mongo_forid_co.stats.swift.find_one_and_update({"type": "object_id_file"},   {"$inc": {"object_id": 1}})[
        "object_id"]


def insert_datalake(file_path,file_name, user, key, authurl, container_name,
                    data_process = "default", description=None,
                    content_type=None,
                    mongodb_url="127.0.0.1:27017", other_data = None,
                    is_compressed = False, internal_type=None):
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
    :param description: Description of the description where the data
    come from or whatever you want
    :type description : str
    :param content_type: MIME Type of the data
    :type content_type : str
    :param mongodb_url: the MongoDB IP_ADDR with Port
    :type mongodb_url : str
    :param data_process : process the data in default pipeline or custom one
    :type data_process : str : "default" or "custom"
    '''
    archive_MIME = ["application/zip", "application/x-7z-compressed",
                    "	application/x-tar", "application/x-rar-compressed",
                    "application/java-archive", "application/x-bzip2",
                    "application/x-bzip"]
    file_full_path = os.path.join(file_path, file_name)
    print(file_full_path)
    file_content = open(file_full_path, "rb").read()
    # TODO : use os.path
    conn = swiftclient.Connection(user=user, key=key,
                                  authurl=authurl)
    client = MongoClient(mongodb_url, connect=False)
    db = client.swift
    coll = db[container_name]
    if content_type is None:
        # TODO : Check MIME type
        magic_obj = magic.Magic(mime=True, uncompress=False)
        content_type = f.from_file(file_full_path)
    ## Construction des méta données
    meta_data = {}
    if content_type is not None:
        meta_data["content_type"] = content_type
    else:
        meta_data["content_type"] = "None"
    meta_data["data_processing"]= data_process
    meta_data["swift_user"] = user
    meta_data["swift_container"] = container_name
    meta_data["swift_object_id"] = str(get_id(mongodb_url))
    if meta_data["content_type"] in archive_MIME or is_compressed :
        meta_data["is_compressed"] = True

        magic_obj = magic.Magic(mime=True, uncompress = True)
        if internal_type :
            meta_data["internal_type"] = internal_type
        else :
            meta_data["internal_type"] = magic_obj.from_file(file_full_path)
            pass
    if description is not None:
        meta_data["description"] = description
    else:
        meta_data["description"] = user + "_" + container_name
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
                            content_type=meta_data["content_type"])
            coll.insert_one(meta_data)
            return None
        except Exception as e:
            print(e)
            retry += 1
            if retry > 3:
                return None


#####################################



user = 'test:tester'
key = 'testing'
mongo_url = globals()["META_MONGO_IP"] + ":" + globals()["MONGO_PORT"]
client = MongoClient(globals()["META_MONGO_IP"] + ":" + globals()["MONGO_PORT"])



authurl = "http://"+ globals()["OPENSTACK_SWIFT_IP"]+":"+globals()["SWIFT_REST_API_PORT"]+"/auth/v1.0"
conn = swiftclient.Connection(user=user, key=key,
                              authurl=authurl)
path = cwd + "/"
file_name = "synop.202011.csv"
file_uri = path+file_name
with open(file_uri , "rb") as f:
    file_data = f.read()

file_content = open(path+file_name, "r")
other_data = {
    "user_uri": "http://melodi.irit.fr/resource/Agent/dn_a160581993488600",
    "dataset_url": "http://localhost:8085/dataset.xhtml?persistentId=doi:10.5072/FK2/ILRD2U",
    "distribution_url": "http://localhost:8085/api/access/datafile/35",
    "dataset_uri": "http://melodi.irit.fr/resource/Dataset/dn_1605874413364",
    "distribution_uri": "http://melodi.irit.fr/resource/Distribution/1605874413364-35",
    "dataset_id": "doi:10.5072/FK2/ILRD2U",
    "subject": "Earth and Environmental Sciences"
}


container_name = "DataNoos"
f = magic.Magic(mime=True, uncompress=False)
insert_datalake(path, file_name, user, key, authurl, container_name, data_process="custom",
                description="DataNoos demo : Meteo France synop weather observations in 11/2020",
                mongodb_url=mongo_url, other_data=other_data, content_type="application/csv"
                )

path = cwd + "/"
file_name = "synop.202011.csv"
file_uri = path+file_name
h = magic.Magic(mime=True, uncompress=True)
print(h.from_file(file_uri))