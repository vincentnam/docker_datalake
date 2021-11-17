import os
import uuid
from zipfile import ZipFile
import base64
from flask import Blueprint, jsonify, current_app, request, send_from_directory
from ..services import swift, mongo
import os
import paramiko
from pathlib import Path

swift_file_bp = Blueprint('swift_file_bp', __name__)


@swift_file_bp.route('/swift-files', methods=['POST'])
def swift_files():
    swift_files = []
    zip_file_name = f'{str(uuid.uuid4().hex)}.zip'
    zip_path = os.path.join(current_app.config['SWIFT_FILES_DIRECTORY'], zip_file_name)
    zip_obj = ZipFile(os.path.join(current_app.root_path, zip_path), 'w')

    for co in request.get_json():
        container_name = co["container_name"]
        object_id = co["object_id"]
        file_path = swift.download_object_file(container_name, object_id)
        swift_files.append({
            "container_name": container_name,
            "object_id": object_id,
            "object_file": os.path.join(request.host_url, file_path)
        })
        zip_obj.write(os.path.join(current_app.root_path, file_path), os.path.basename(file_path))
    zip_obj.close()

    result = {
        'swift_files': swift_files,
        'swift_zip': os.path.join(request.host_url, zip_path),
    }
    return jsonify(result)


@swift_file_bp.route('/cache-swift-files/<path:filename>')
def download(filename):
    swift_files_directory = os.path.join(current_app.root_path, current_app.config['SWIFT_FILES_DIRECTORY'])
    return send_from_directory(directory=swift_files_directory, filename=filename)

@swift_file_bp.route('/storage', methods=['POST'])
def storage():
    # id_type = request.get_json()["idType"]
    file = request.get_json()["file"]
    filename = request.get_json()["filename"]
    other_meta = request.get_json()["othermeta"]
    type_file = request.get_json()["typeFile"]

    data_file = file.split(",")
    data_file = data_file[1]
    data_file = base64.b64decode(data_file)

    # FIXME : put in DAG to Apache Airflow handling and get picture content from MongoDB
    # Else pictures will not be printed after download

    #data_file = str(data_file)
    #data_file = data_file.split("'")
    #file_content = ''.join(map(str.capitalize, data_file[1:]))
    
    file_content = data_file

    container_name = "neOCampus"
    mongodb_url = current_app.config['MONGO_URL']
    user = current_app.config['SWIFT_USER']
    key = current_app.config['SWIFT_KEY']
    authurl = current_app.config['SWIFT_AUTHURL']
    content_type = type_file
    application = None
    data_process = "custom"
    processed_data_area_service = ["MongoDB"]
    other_data = other_meta
    
    mongo.insert_datalake(file_content, user, key, authurl, container_name, filename,
                        processed_data_area_service, data_process, application,
                        content_type, mongodb_url, other_data)

    return jsonify({"response": "Done !"})

@swift_file_bp.route('/register-sge-file', methods=['POST'])
def sge_file():
    sge_ip_address = "10.200.156.253"
    host_key = "AAAAE2VjZHNhLXNoYTItbmlzdHAyNTYAAAAIbmlzdHAyNTYAAABBBHJdWchwbWG661xt2c53FP2LRXV3vwJ0OaqCpkVe7LoYmuD8BlfxgDVvDt5ZtveMaKu4XjmR7DRY6tV2i7KhDOw="
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    from base64 import decodebytes

    transport = paramiko.Transport(sge_ip_address)
    transport.get_security_options().key_types = ["ecdsa-sha2-nistp256"]

    #keydata = b""""""
    keydata = current_app.config['SSH_KEY']
    key = paramiko.ECDSAKey(data=decodebytes(keydata))

    ssh.load_system_host_keys()
    ssh.connect(
        sge_ip_address, 
        username=current_app.config['SGE_USERNAME'], 
        password=current_app.config['SGE_PASSWORD']
    )
    sftp = ssh.open_sftp()
    filename = ""
    localpath = '/home/'
    remotepath = current_app.config['SGE_REMOTE_PATH']+filename
    sftp.get(remotepath, localpath)
    sftp.close()
    ssh.close()

    data_file = Path(localpath).read_text()
    filename = data_file.name

    data_file = base64.b64decode(data_file)
    file_content = data_file

    container_name = "neOCampus"
    mongodb_url = current_app.config['MONGO_URL']
    user = current_app.config['SWIFT_USER']
    key = current_app.config['SWIFT_KEY']
    authurl = current_app.config['SWIFT_AUTHURL']
    content_type = "application/octet-stream"
    application = None
    data_process = "default"
    processed_data_area_service = ["MongoDB"]
    other_data = "sge_data"
    
    mongo.insert_datalake(file_content, user, key, authurl, container_name, filename,
                        processed_data_area_service, data_process, application,
                        content_type, mongodb_url, other_data)