import os
import uuid
from zipfile import ZipFile
import base64
from flask import Blueprint, jsonify, current_app, request, send_from_directory
from ..services import swift, mongo

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
    link_file = request.get_json()["linkFile"]
    link_type = request.get_json()["linkType"]
    
    if link_file != "":        
        link = link_file.split('/')
        path = ""
        if link_type == "http":
            link_http = link[0]
            path = "/" + "/".join(link[3:])
        else:
            link_ip = link[0]
            path = "/" + "/".join(link[1:])
        
        if type_file == "application/octet-stream":
            print("SGE")
            if link_type == "http":
                print(link_http)
                print(path)
            else:
                print(link_ip)
                print(path)
        
        else:
            print("Other type file")
            if link_type == "http":
                print(link_http)
                print(path)
            else:
                print(link_ip)
                print(path)
        
    else:
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