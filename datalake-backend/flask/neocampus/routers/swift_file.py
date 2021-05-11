import os
import uuid
from zipfile import ZipFile
from flask import Blueprint, jsonify, current_app, request, send_from_directory
from ..services import swift

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
    idType = request.get_json()["idType"]
    file =  request.get_json()["file"]
    premieremeta =  request.get_json()["premieremeta"]
    deuxiememeta =  request.get_json()["deuxiememeta"]
    typeFile =  request.get_json()["typeFile"]
    meta = dict()
    meta = {
        "idT": idType,
        "file": file,
        "typeFile": typeFile,
        "meta1": premieremeta,
        "meta2": deuxiememeta
    }
    
    meta = request.get_json()
    
    print(meta)
    
    # resultMongo = mongo.add_data_in_collection('neocampus', meta)

    return jsonify(meta)

