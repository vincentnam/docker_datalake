import os

import swiftclient
from flask import current_app
from .mongo import get_swift_original_object_name
from ..services import mongo
import paramiko
from pathlib import Path
from pymongo import MongoClient
from bson.objectid import ObjectId
import datetime

def download_object_file(container_name, object_id):
    """
    convert swift object to file and down it
    :param container_name: swift container name
    :param object_id: swift object id
    :return: saved file path in flask
    """
    swift_conn = swiftclient.Connection(user=current_app.config['SWIFT_USER'], key=current_app.config['SWIFT_KEY'],
                                        authurl=current_app.config['SWIFT_AUTHURL'], insecure=True)
    swift_object_raw = swift_conn.get_object(container_name, object_id)

    original_object_name = get_swift_original_object_name(container_name, object_id)

    # save file
    file_path = f"{current_app.config['SWIFT_FILES_DIRECTORY']}/{original_object_name}"
    f = open(os.path.join(current_app.root_path, file_path), 'wb')
    f.write(swift_object_raw[1])
    f.close()

    return file_path

def ssh_file(
    address,
    username,
    password,
    remote_path,
    filename,
    type_file,
    container_name
    ):
    try:
        ssh = paramiko.SSHClient()

        # For host key - Add it automatically to known_hosts
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        ssh.load_system_host_keys()

        # Connect to server throughout SSH protocol
        ssh.connect(
            address, 
            username=username,
            password=password
        )
        sftp = ssh.open_sftp()
        # Localpath -> Locally in Docker container
        localpath = '/home/'+filename

        # Remote path on the server to find the file
        remotepath = remote_path
        
        #Connection to mongodb and variable for calback function
        mongodb_url = current_app.config['MONGO_URL']
        mongo_client = MongoClient(mongodb_url, username=current_app.config['MONGO_ADMIN'], password=current_app.config['MONGO_PWD'], authSource=current_app.config['MONGO_DB_AUTH'], connect=False)
        mongo_db = mongo_client.upload
        mongo_collection = mongo_db["file_upload"]
        new_value = True
        id_file_upload = ""
        #Callback function
        def callback_large_file_upload(transferred, toBeTransferred):
            nonlocal new_value
            nonlocal id_file_upload
            
            # date = dt.strptime(dt.now(tz=None), '%Y-%m-%d')
            if new_value == True:
                data = {
                    "filename": filename,
                    "type_file": type_file,
                    "total_bytes_download": transferred,
                    "total_bytes": toBeTransferred,
                    "created_at": datetime.datetime.now(),
                    "update_at": datetime.datetime.now(),
                    "container_name": container_name,
                }
                id_file_upload = mongo_collection.insert_one(data).inserted_id
                new_value = False
            else:
                doc = {"_id": ObjectId(id_file_upload)}
                newvalues = { "$set": { "total_bytes_download": transferred, "update_at": datetime.datetime.now() } }
                mongo_collection.update_one(doc, newvalues)

        # Get and download it locally
        sftp.get(remotepath, localpath,callback=callback_large_file_upload)
        sftp.close()
        ssh.close()

        path =  Path(localpath)
        
        if type_file == "application/octet-stream":
            content_file = path.read_bytes()
        else:
            content_file = path.read_text()
        filename = path.name

        file_content = content_file
        
        # All variables to put informations in MongoDB
        # and in OpenstackSwift
        mongodb_url = current_app.config['MONGO_URL']
        user = current_app.config['SWIFT_USER']
        key = current_app.config['SWIFT_KEY']
        authurl = current_app.config['SWIFT_AUTHURL']
        content_type = type_file
        application = None
        data_process = "default"
        processed_data_area_service = ["MongoDB"]
        other_data = {
            "type_link": "ssh"
        }
        mongo.insert_datalake(file_content, user, key, authurl, container_name, filename,
                            processed_data_area_service, data_process, application,
                            content_type, mongodb_url, other_data)
        
        return "OK"
    except Exception as e:
        print(e)
        return "Problem"