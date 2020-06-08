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
