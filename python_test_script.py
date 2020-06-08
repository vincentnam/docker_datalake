from pymongo import MongoClient
#
# client = MongoClient("127.0.0.1:27017")
# db = client.test
# coll = db.test
# post = {"author": "Mike",
#          "text": "My first blog post!",
#          "tags": ["mongodb", "python", "pymongo"]}
#
# coll.insert_one(post)
#
#

import swiftclient.service
from swiftclient.service import SwiftService
# docs.ceph.com/docs/jewel/radosgw/swift/python


user='test:tester'
key = 'testing'
#
# conn = swiftclient.Connection(user=user,key=key,authurl="http://127.0.0.1:12345/auth/v1.0")
# container_name = 'my-new-container'
# #
# # with open("input_file_test/"+"0.jpg","rb") as f :
# #     file_data = f.read()
# # conn.put_object(container_name, "input_file_test/"+"0.jpg", contents=file_data
# #                         ,content_type="image/jpg")
# #
# # obj = conn.get_object(container_name,"input_file_test/"+"0.jpg")
# #
# # with open("return_file.png",'wb') as my_image :
# #     my_image.write(obj[1])
# # # with open('requirements.txt', 'r') as hello_file:
# # #     conn.put_object(container_name, 'hello.txt',
# # #                     contents=hello_file.read(),
# # #                     content_type='text/plain')
# #
# # # for container in conn.get_account()[1]:
# # #         print (container['name'])
# # for data in conn.get_container(container_name)[1]:
# #         print ('{0}\t{1}\t{2}'.format(data['name'], data['bytes'], data['last_modified']))
# #         print(data)
# #
#
# conn.put_object(container_name,post,contents=post, content_type="application/json")

import swiftclient.service

# user='test:tester'
# key = 'testing'
#
# conn = swiftclient.Connection(user=user,key=key,authurl="http://127.0.0.1:12345/auth/v1.0")
# container_name = 'my-new-container'



# Container_name is the same as a collection name in mongodb

def get_id(mongodb_url):
    mongo_forid_co = MongoClient(mongodb_url)
    return mongo_forid_co.stats.swift.find_one({"type":"object_id_file"})["object_id"]


def insert_datalake(file_content, file_name,meta_data, user, key, authurl, container_name, mongodb_url="127.0.0.1:27017"):
    '''
    :param file: name OR the file : it has to be defined to be sure of what data are stored in mongodb
    :param meta_data: dict
    :param user:
    :param key:
    :param authurl:
    :param container_name: used for collection name
    :return:
    '''
    conn = swiftclient.Connection(user=user, key=key,
                                  authurl=authurl)
    # container_name = 'my-new-container'
    # with open("input_file_test/" + "0.jpg", "rb") as f:
    # file_data = f.read()
    client = MongoClient(mongodb_url)
    db = client.swift
    coll = db[container_name]
    meta_data["swift_user"]=user
    meta_data["swift_container"] = container_name
    meta_data["swift_object_id"] = str(get_id(mongodb_url))
    meta_data["swift_object_name"] = file_name
    print(meta_data)

    if SwiftService({}).stat(container_name)["object"] is None:
        conn.put_container(container_name)
# Gérer l'atomicité de cette partie #
    conn.put_object(container_name, meta_data["swift_object_id"], contents=file_content,
                    content_type=meta_data["content_type"])

    coll.insert_one(meta_data)
    client.stats.swift.update_one({"type":"object_id_file"},
                                  {"$inc": {"object_id": 1}})
#####################################

def init_id():
    # USE IT ONLY ONE TIME !!
    id_doc = {"type": "object_id_file", "object_id": 0}
    client = MongoClient("127.0.0.1:27017").stats.swift
    client.insert_one(id_doc)
    client.create_index("type", unique=True)


# client = MongoClient("127.0.0.1:27017").stats.swift.drop()
# init_id()
# client = MongoClient("127.0.0.1:27017")

# id_doc =  {"type":"object_id_file", "object_id":0}
# client = MongoClient("127.0.0.1:27017").stats.swift.insert_one(id_doc)
# print(get_id("127.0.0.1:27017"))


import requests
authurl = "http://127.0.0.1:12345/auth/v1.0"
conn = swiftclient.Connection(user=user, key=key,
                              authurl=authurl)

file_name = "Openstack/swift/input_file_test/0.png"
meta_data = {
    "content_type": "image/png",
    "application": "mygates cnn"
}
# with open(file_name,"rb") as f :
#     file_data = f.read()
with open(file_name,"rb") as f:
    file_data = f.read()

file_content = open(file_name, "r")
print(file_data)
container_name = "mygates"
#
# conn.put_object(container_name,"0.jpg", contents=file_data
#                         ,content_type="image/jpg")

insert_datalake(file_data, file_name,meta_data, user, key, authurl, container_name, mongodb_url="127.0.0.1:27017")
# conn.put_container(container_name)

# datalake_input_swift_1         | Jun  3 17:32:32 c9d68540141e container-sync: UNCAUGHT EXCEPTION#012Traceback (most recent call last):#012  File "/usr/bin/swift-container-sync", line 23, in <module>#012    run_daemon(ContainerSync, conf_file, **options)#012  File "/usr/lib/python2.7/dist-packages/swift/common/daemon.py", line 110, in run_daemon#012    klass(conf).run(once=once, **kwargs)#012  File "/usr/lib/python2.7/dist-packages/swift/common/daemon.py", line 57, in run#012    self.run_forever(**kwargs)#012  File "/usr/lib/python2.7/dist-packages/swift/container/sync.py", line 173, in run_forever#012    for path, device, partition in all_locs:#012  File "/usr/lib/python2.7/dist-packages/swift/common/utils.py", line 1721, in audit_location_generator#012    partitions = listdir(datadir_path)#012  File "/usr/lib/python2.7/dist-packages/swift/common/utils.py", line 2160, in listdir#012    return os.listdir(path)#012OSError: [Errno 20] Not a directory: '/srv/object.ring.gz/containers'
# datalake_middleware_airflow_1  | [2020-06-03 17:32:36 +0000] [50] [INFO] Handling signal: ttin
# datalake_middleware_airflow_1  | [2020-06-03 17:32:36 +0000] [16964] [INFO] Booting worker with pid: 16964
# datalake_middleware_airflow_1  | [2020-06-03 17:32:36,587] {__init__.py:51} INFO - Using executor SequentialExecutor
# datalake_middleware_airflow_1  | [2020-06-03 17:32:36,587] {dagbag.py:403} INFO - Filling up the DagBag from /usr/local/airflow/dags
# datalake_middleware_airflow_1  | [2020-06-03 17:32:37 +0000] [50] [INFO] Handling signal: ttou
# datalake_middleware_airflow_1  | [2020-06-03 17:32:37 +0000] [16853] [INFO] Worker exiting (pid: 16853)
# datalake_input_swift_1         | Jun  3 17:32:37 c9d68540141e object-replicator: Starting object replication pass.
# datalake_input_swift_1         | Jun  3 17:32:37 c9d68540141e object-replicator: Nothing replicated for 0.00133919715881 seconds.
# datalake_input_swift_1         | Jun  3 17:32:37 c9d68540141e object-replicator: Object replication complete. (0.00 minutes)
