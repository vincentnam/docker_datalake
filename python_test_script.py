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


def init_id():
    # USE IT ONLY ONE TIME !!
    id_doc = {"type": "object_id_file", "object_id": 0}
    client = MongoClient("127.0.0.1:27017").stats.swift
    if  MongoClient("127.0.0.1:27017").stats.swift.find_one(
        {"type": "object_id_file"}) is None:
        client.insert_one(id_doc)
    client.create_index("type", unique=True)

def clean_swift(container):
    pass

def insert_datalake(file_content,meta_data, user, key, authurl, container_name, mongodb_url="127.0.0.1:27017"):
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
    # meta_data["swift_object_name"] = file_name
    print(meta_data)

    URL = "http://141.115.103.32:8080"
    ENDPOINT_PATH = "/api/experimental"
    DAG_TO_TRIGGER = "new_input"
    if SwiftService({}).stat(container_name)["object"] is None:
        conn.put_container(container_name)
# Gérer l'atomicité de cette partie #

    coll.insert_one(meta_data)
    client.stats.swift.update_one({"type":"object_id_file"},
                                  {"$inc": {"object_id": 1}})
    conn.put_object(container_name, meta_data["swift_object_id"], contents=file_content,
                    content_type=meta_data["content_type"], headers={"x-webhook":URL + ENDPOINT_PATH + "/dags/"+DAG_TO_TRIGGER+"/dag_runs"})

#####################################
import pandas as pd
import os
import mimetypes
import bsonnumpy
def input_csv_file(csv_file,**kwargs):
    df = pd.read_csv(csv_file, sep=kwargs["sep"], header=kwargs["header"])
    print(df.keys())
    # print(df["path"]+df["file_name"])
    # print(df["extension"])
    for i in df.iloc:
        meta_data = {
            "content_type": mimetypes.guess_type(i["file_name"])[0],
            "projet": kwargs["projet"],
        }

        print(type(i["main_object"]))
        for j in i.keys() :
            meta_data[j]=str(i[j])
        print(meta_data)
        # print(meta_data)
        # print(mimetypes.guess_type("file" + i))
    # print(mimetypes.guess_type("file" + ".jpg"))
        with open(os.path.join(meta_data["path"],meta_data["file_name"]), "rb") as f:
             file_data = f.read()
        insert_datalake(file_data, meta_data, user, key, kwargs["authurl"],
                        kwargs["container_name"], mongodb_url="127.0.0.1:27017")
        break
# TODO: Finir le JSON des fichiers
# TODO : réparer l'ajout de listes dans mongodb
# TODO : Voire pour la segmentation d'image (https://github.com/facebookresearch/Detectron2)




# def test():
#     from swiftclient.service import SwiftService
#     print(SwiftService().list(container="mygates"))




user='test:tester'
key = 'testing'

# client = MongoClient("127.0.0.1:27017").stats.swift.drop()
client = MongoClient("127.0.0.1:27017")
# init_id()

# id_doc =  {"type":"object_id_file", "object_id":0}
# client = MongoClient("127.0.0.1:27017").stats.swift.insert_one(id_doc)
# print(get_id("127.0.0.1:27017"))

#
# import requests
authurl = "http://127.0.0.1:8080/auth/v1.0"
conn = swiftclient.Connection(user=user, key=key,
                              authurl=authurl)
#
#
file_name = "Openstack/swift/input_file_test/log.json"
meta_data = {
    "content_type": "application/json",
    "application": "neocampus sensors log"
}
# with open(file_name,"rb") as f :
#     file_data = f.read()
with open(file_name,"rb") as f:
    file_data = f.read()

file_content = open(file_name, "r")
print(file_data)
container_name = "neocampus"
#https://github.com/vincentnam/docker_datalake
# conn.put_object(container_name,"0.jpg", contents=file_data
#                         ,content_type="image/jpg")

# conn.put_container(container_name)
insert_datalake(file_data,meta_data, user, key, authurl, container_name, mongodb_url="127.0.0.1:27017")





# Error: An error occurred:
#012Traceback (most recent call last):
# #012  File "/usr/lib/python2.7/dist-packages/swift/common/middleware/catch_errors.py", line 36, in handle_request#012
# resp = self._app_call(env)
# 012  File "/usr/lib/python2.7/dist-packages/swift/common/wsgi.py", line 522, in _app_call#012
# resp = self.app(env, self._start_response)
# #012  File "/usr/lib/python2.7/dist-packages/swift/common/middleware/gatekeeper.py", line 90, in __call__#012
# return self.app(env, gatekeeper_response)
# #012  File "/usr/lib/python2.7/dist-packages/swift/common/middleware/healthcheck.py", line 57, in __call__#012
# return self.app(env, start_response)
# #012  File "/usr/lib/python2.7/dist-packages/swift/common/middleware/proxy_logging.py", line 290, in __call__
# #012    iterable = self.app(env, my_start_response)
# #012  File "/usr/lib/python2.7/dist-packages/swift/common/middleware/memcache.py", line 85, in __call__
# #012  return self.app(env, start_response)
# #012  File "/usr/lib/python2.7/dist-packages/swift/common/swob.py", line 1265, in _wsgify_self
# #012    return func(self, Request(env))(env, start_response)
# #012  File "/usr/lib/python2.7/dist-packages/swift/common/middleware/tempurl.py", line 274, in __call__
# #012    return self.app(env, start_response)
# #012  File "/usr/lib/python2.7/dist-packages/swift/common/middleware/slo.py", line 751, in __call__
# #012    return self.app(env, start_response)
# #012  File "/usr/lib/python2.7/dist-packages/swift/common/middleware/dlo.py", line 285, in __call__
# #012    return self.app(env, start_response)
# #012  File "/usr/lib/python2.7/dist-packages/swift/common/middleware/ratelimit.py", line 279, in __call__
# #012    ratelimit_resp = self.handle_ratelimit(req, account, container, obj)
# #012  File "/usr/lib/python2.7/dist-packages/swift/common/middleware/ratelimit.py", line 237, in handle_ratelimit
# #012    obj_name=obj_name):
# #012  File "/usr/lib/python2.7/dist-packages/swift/common/middleware/ratelimit.py", line 163, in get_ratelimitable_key_tuples
# #012    account_info = get_account_info(req.environ, self.app)
# #012  File "/usr/lib/python2.7/dist-packages/swift/proxy/controllers/base.py", line 312, in get_account_info
# #012    swift_source=swift_source)
# #012  File "/usr/lib/python2.7/dist-packages/swift/proxy/controllers/base.py", line 519, in get_info
# #012    resp = req.get_response(app)
# #012  File "/usr/lib/python2.7/dist-packages/swift/common/swob.py", line 936, in get_response
# #012    status, headers, app_iter = self.call_application(application)
# #012  File "/usr/lib/python2.7/dist-packages/swift/common/swob.py", line 922, in call_application
# #012    app_iter = application(self.environ, start_response)
# #012  File "/usr/lib/python2.7/dist-packages/swift/common/middleware/crossdomain.py", line 82, in __call__
# #012    return self.app(env, start_response)
# #012  File "/usr/lib/python2.7/dist-packages/swift/common/middleware/tempauth.py", line 175, in __call__
# #012    return self.app(env, start_response)
# #012  File "/usr/lib/python2.7/dist-packages/swift/common/middleware/staticweb.py", line 482, in __call__
# #012    return self.app(env, start_response)
# #012  File "/usr/lib/python2.7/dist-packages/swift/common/swob.py", line 1265, in _wsgify_self
# 012    return func(self, Request(env))(env, start_response)
# #012  File "/usr/lib/python2.7/dist-packages/swift/common/swob.py", line 1265, in _wsgify_self
# #012    return func(self, Request(env))(env, start_response)
# #012  File "/usr/lib/python2.7/dist-packages/swift/common/middleware/proxy_logging.py", line 290, in __call__
# #012    iterable = self.app(env, my_start_response)
# #012  File "/usr/lib/python2.7/dist-packages/swift/common/swob.py", line 1265, in _wsgify_self
# #012    return func(self, Request(env))(env, start_response)
# #012TypeError: 'NoneType' object is not callable (txn: txfc736ee8b3aa47f9b3e42-005edfad5a)











#
#
#
#
#
#
#
# atalake_input_swift_1         | Jun  9 16:33:24 8d7c5235a89c proxy-server: STDOUT: <swift.common.swob.Request object at 0x7f52bf099850> (txn: tx69288e68ec21447593504-005edfb9d4)
# datalake_input_swift_1         | Jun  9 16:33:24 8d7c5235a89c proxy-server: STDOUT: {'Host': '127.0.0.1:12345', 'User-Agent': 'Swift'} (txn: tx69288e68ec21447593504-005edfb9d4)
# datalake_input_swift_1         | Jun  9 16:33:24 8d7c5235a89c proxy-server: STDOUT: {'wsgi.multithread': False, 'SCRIPT_NAME': '', 'wsgi.input': <swift.common.utils.InputProxy object at 0x7f52bf099890>, 'REQUEST_METHOD': 'HEAD', 'HTTP_HOST': '127.0.0.1:12345', 'PATH_INFO': '/v1/AUTH_test', 'staticweb.start_time': 1591720404.407186, 'SERVER_PROTOCOL': 'HTTP/1.0', 'QUERY_STRING': '', 'swift.authorize': <function <lambda> at 0x7f52bf09b758>, 'swift.source': 'GET_INFO', 'HTTP_USER_AGENT': 'Swift', 'wsgi.version': (1, 0), 'eventlet.posthooks': [], 'SERVER_NAME': '172.19.0.4', 'wsgi.errors': <cStringIO.StringI object at 0x7f52bf146140>, 'wsgi.multiprocess': False, 'swift.trans_id': 'tx69288e68ec21447593504-005edfb9d4', 'wsgi.url_scheme': 'http', 'swift.proxy_access_log_made': True, 'REMOTE_USER': '.wsgi.pre_authed', 'SERVER_PORT': '8080', 'swift.cache': <swift.common.memcached.MemcacheRing object at 0x7f52bf124e90>, 'swift.authorize_override': True}
#
#
#
#
# datalake_input_swift_1         | Jun  9 16:33:24 8d7c5235a89c proxy-server: STDOUT: <swift.common.swob.Request object at 0x7f52bf099a90> (txn: tx69288e68ec21447593504-005edfb9d4)
# datalake_input_swift_1         | Jun  9 16:33:24 8d7c5235a89c proxy-server: STDOUT: {'Content-Length': '0', 'Accept-Encoding': 'identity', 'User-Agent': 'python-swiftclient-3.9.0', 'Host': '127.0.0.1:12345', 'X-Auth-Token': 'AUTH_tk3bb3323733b24d7690d876babcedd8a4', 'Content-Type': None} (txn: tx69288e68ec21447593504-005edfb9d4)
# datalake_input_swift_1         | Jun  9 16:33:24 8d7c5235a89c proxy-server: STDOUT: {'SCRIPT_NAME': '', 'swift.proxy_access_log_made': True, 'REQUEST_METHOD': 'PUT', 'PATH_INFO': '/v1/AUTH_test/mygatess', 'staticweb.start_time': 1591720404.410575, 'SERVER_PROTOCOL': 'HTTP/1.0', 'swift.authorize': <bound method TempAuth.authorize of <swift.common.middleware.tempauth.TempAuth object at 0x7f52bf11e9d0>>, 'REMOTE_ADDR': '172.19.0.1', 'CONTENT_LENGTH': '0', 'HTTP_X_AUTH_TOKEN': 'AUTH_tk3bb3323733b24d7690d876babcedd8a4', 'HTTP_USER_AGENT': 'python-swiftclient-3.9.0', 'eventlet.posthooks': [], 'RAW_PATH_INFO': '/v1/AUTH_test/mygatess', 'REMOTE_PORT': '41196', 'eventlet.input': <eventlet.wsgi.Input object at 0x7f52bf14a7d0>, 'wsgi.url_scheme': 'http', 'swift.account/AUTH_test': {'status': 204, 'container_count': 2, 'bytes': '230605', 'total_object_count': '3', 'meta': {}, 'sysmeta': {}}, 'SERVER_PORT': '8080', 'wsgi.input': <swift.common.utils.InputProxy object at 0x7f52bf099b50>, 'REMOTE_USER': 'test,test:tester,AUTH_test', 'HTTP_HOST': '127.0.0.1:12345', 'swift.cache': <swift.common.memcached.MemcacheRing object at 0x7f52bf124e90>, 'wsgi.multithread': True, 'wsgi.version': (1, 0), 'SERVER_NAME': '172.19.0.4', 'GATEWAY_INTERFACE': 'CGI/1.1', 'wsgi.run_once': False, 'wsgi.errors': <swift.common.utils.LoggerFileObject object at 0x7f52bf158d10>, 'wsgi.multiprocess': False, 'swift.trans_id': 'tx69288e68ec21447593504-005edfb9d4', 'CONTENT_TYPE': None, 'swift.clean_acl': <function clean_acl at 0x7f52bfa51488>, 'HTTP_ACCEPT_ENCODING': 'identity'}
#
#
#
#
# datalake_input_swift_1         | Jun  9 16:33:24 8d7c5235a89c proxy-server: STDOUT: <swift.common.swob.Request object at 0x7f52bf0a9490> (txn: txb3e285ffd6ce497fbb283-005edfb9d4)
# datalake_input_swift_1         | Jun  9 16:33:24 8d7c5235a89c proxy-server: STDOUT: {'Content-Length': '0', 'Accept-Encoding': 'identity', 'User-Agent': 'python-swiftclient-3.9.0', 'Host': '127.0.0.1:12345', 'X-Auth-Token': 'AUTH_tk3bb3323733b24d7690d876babcedd8a4', 'Content-Type': None} (txn: txb3e285ffd6ce497fbb283-005edfb9d4)
# datalake_input_swift_1         | Jun  9 16:33:24 8d7c5235a89c proxy-server: STDOUT: {'SCRIPT_NAME': '', 'swift.proxy_access_log_made': True, 'REQUEST_METHOD': 'PUT', 'PATH_INFO': '/v1/AUTH_test/mygatess', 'staticweb.start_time': 1591720404.452821, 'SERVER_PROTOCOL': 'HTTP/1.0', 'swift.authorize': <bound method TempAuth.authorize of <swift.common.middleware.tempauth.TempAuth object at 0x7f52bf11e9d0>>, 'REMOTE_ADDR': '172.19.0.1', 'CONTENT_LENGTH': '0', 'HTTP_X_AUTH_TOKEN': 'AUTH_tk3bb3323733b24d7690d876babcedd8a4', 'HTTP_USER_AGENT': 'python-swiftclient-3.9.0', 'eventlet.posthooks': [], 'RAW_PATH_INFO': '/v1/AUTH_test/mygatess', 'REMOTE_PORT': '41222', 'eventlet.input': <eventlet.wsgi.Input object at 0x7f52bf099c90>, 'wsgi.url_scheme': 'http', 'swift.account/AUTH_test': {'status': 204, 'container_count': 2, 'bytes': '230605', 'total_object_count': '3', 'meta': {}, 'sysmeta': {}}, 'SERVER_PORT': '8080', 'wsgi.input': <swift.common.utils.InputProxy object at 0x7f52bf0a9150>, 'REMOTE_USER': 'test,test:tester,AUTH_test', 'HTTP_HOST': '127.0.0.1:12345', 'swift.cache': <swift.common.memcached.MemcacheRing object at 0x7f52bf124e90>, 'wsgi.multithread': True, 'wsgi.version': (1, 0), 'SERVER_NAME': '172.19.0.4', 'GATEWAY_INTERFACE': 'CGI/1.1', 'wsgi.run_once': False, 'wsgi.errors': <swift.common.utils.LoggerFileObject object at 0x7f52bf158d10>, 'wsgi.multiprocess': False, 'swift.trans_id': 'txb3e285ffd6ce497fbb283-005edfb9d4', 'CONTENT_TYPE': None, 'swift.clean_acl': <function clean_acl at 0x7f52bfa51488>, 'HTTP_ACCEPT_ENCODING': 'identity'}
#
#
#
#
# datalake_input_swift_1         | Jun  9 16:33:24 8d7c5235a89c proxy-server: STDOUT: <swift.common.swob.Request object at 0x7f52bf099b10> (txn: txf12a4c77054440d794f4b-005edfb9d4) (client_ip: 172.19.0.1)
# datalake_input_swift_1         | Jun  9 16:33:24 8d7c5235a89c proxy-server: STDOUT: {'Host': '127.0.0.1:12345', 'User-Agent': 'Swift'} (txn: txf12a4c77054440d794f4b-005edfb9d4) (client_ip: 172.19.0.1)
# datalake_input_swift_1         | Jun  9 16:33:24 8d7c5235a89c proxy-server: STDOUT: {'wsgi.multithread': False, 'SCRIPT_NAME': '', 'wsgi.input': <swift.common.utils.InputProxy object at 0x7f52bf0997d0>, 'REQUEST_METHOD': 'HEAD', 'HTTP_HOST': '127.0.0.1:12345', 'PATH_INFO': '/v1/AUTH_test/mygatess', 'SERVER_PROTOCOL': 'HTTP/1.0', 'QUERY_STRING': '', 'swift.authorize': <function <lambda> at 0x7f52bf09b578>, 'eventlet.posthooks': [], 'swift.source': 'CQ', 'REMOTE_USER': '.wsgi.pre_authed', 'wsgi.version': (1, 0), 'HTTP_USER_AGENT': 'Swift', 'SERVER_NAME': '172.19.0.4', 'wsgi.errors': <cStringIO.StringI object at 0x7f52bf146140>, 'wsgi.multiprocess': False, 'swift.trans_id': 'txf12a4c77054440d794f4b-005edfb9d4', 'wsgi.url_scheme': 'http', 'swift.proxy_access_log_made': True, 'SERVER_PORT': '8080', 'swift.cache': <swift.common.memcached.MemcacheRing object at 0x7f52bf124e90>, 'swift.authorize_override': True} (client_ip: 172.19.0.1)
#
#
#
# datalake_input_swift_1         | Jun  9 16:33:24 8d7c5235a89c proxy-server: STDOUT: <swift.common.swob.Request object at 0x7f52bf099c90> (txn: txf12a4c77054440d794f4b-005edfb9d4)
# datalake_input_swift_1         | Jun  9 16:33:24 8d7c5235a89c proxy-server: STDOUT: {'Content-Length': '230605', 'Accept-Encoding': 'identity', 'User-Agent': 'python-swiftclient-3.9.0', 'Host': '127.0.0.1:12345', 'X-Auth-Token': 'AUTH_tk3bb3323733b24d7690d876babcedd8a4', 'Content-Type': 'image/png'} (txn: txf12a4c77054440d794f4b-005edfb9d4)
# datalake_input_swift_1         | Jun  9 16:33:24 8d7c5235a89c proxy-server: STDOUT: {'swift.copy_hook': <function dlo_copy_hook at 0x7f52bf09b6e0>, 'SCRIPT_NAME': '', 'swift.proxy_access_log_made': True, 'REQUEST_METHOD': 'PUT', 'PATH_INFO': '/v1/AUTH_test/mygatess/5', 'staticweb.start_time': 1591720404.48724, 'SERVER_PROTOCOL': 'HTTP/1.0', 'swift.authorize': <bound method TempAuth.authorize of <swift.common.middleware.tempauth.TempAuth object at 0x7f52bf11e9d0>>, 'REMOTE_ADDR': '172.19.0.1', 'CONTENT_LENGTH': '230605', 'HTTP_X_AUTH_TOKEN': 'AUTH_tk3bb3323733b24d7690d876babcedd8a4', 'HTTP_USER_AGENT': 'python-swiftclient-3.9.0', 'eventlet.posthooks': [], 'RAW_PATH_INFO': '/v1/AUTH_test/mygatess/5', 'REMOTE_PORT': '41222', 'eventlet.input': <eventlet.wsgi.Input object at 0x7f52bf14a5d0>, 'wsgi.url_scheme': 'http', 'swift.account/AUTH_test': {'status': 204, 'container_count': 2, 'bytes': '230605', 'total_object_count': '3', 'meta': {}, 'sysmeta': {}}, 'SERVER_PORT': '8080', 'wsgi.input': <swift.common.utils.InputProxy object at 0x7f52bf14a490>, 'REMOTE_USER': 'test,test:tester,AUTH_test', 'HTTP_HOST': '127.0.0.1:12345', 'swift.cache': <swift.common.memcached.MemcacheRing object at 0x7f52bf124e90>, 'wsgi.multithread': True, 'wsgi.version': (1, 0), 'SERVER_NAME': '172.19.0.4', 'GATEWAY_INTERFACE': 'CGI/1.1', 'wsgi.run_once': False, 'wsgi.errors': <swift.common.utils.LoggerFileObject object at 0x7f52bf158d10>, 'wsgi.multiprocess': False, 'swift.trans_id': 'txf12a4c77054440d794f4b-005edfb9d4', 'swift.container/AUTH_test/mygatess': {'status': 204, 'sync_key': None, 'sysmeta': {}, 'meta': {}, 'write_acl': None, 'object_count': '1', 'versions': None, 'bytes': '230605', 'read_acl': None, 'cors': {'allow_origin': None, 'expose_headers': None, 'max_age': None}}, 'CONTENT_TYPE': 'image/png', 'swift.clean_acl': <function clean_acl at 0x7f52bfa51488>, 'HTTP_ACCEPT_ENCODING': 'identity'}
# datalake_input_swift_1         | Jun  9 16:33:24 8d7c5235a89c proxy-server: <swift.common.swob.Request object at 0x7f52bf099c90>



# Context des requests HTML
# https://airflow.readthedocs.io/en/stable/_modules/airflow/models/dagrun.html#DagRun.conf



# TODO : Changer le webhook par un trigger toutes les X minutes pour tester les données à traiter : mettre dans mongodb la liste des données à traiter

# input_csv_file("./dataset/mygates/subset.csv", sep=";", header=0, projet="mygates",authurl = "http://127.0.0.1:12345/auth/v1.0",container_name = "mygates")

# swift stat -U test:tester -A http://localhost:8080/auth/v1.0 -K testing CONTAINER

# sshfs vdang@co2-dl-airflow:/projets/datalake/airflow/ /data/python-project/docker_datalake/mnt_temp