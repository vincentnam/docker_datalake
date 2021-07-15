import os
import uuid
from zipfile import ZipFile
import base64
from flask import Blueprint, jsonify, current_app, request, send_from_directory
from ..services import swift, mongo, typefile
import tempfile


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

    # TODO : see why it was necessary 

    #data_file = str(data_file)
    #data_file = data_file.split("'")
    #file_content = ''.join(map(str.capitalize, data_file[1:]))
    
    container_name = "neOCampus"
    mongodb_url = current_app.config['MONGO_URL']
    user = current_app.config['SWIFT_USER']
    key = current_app.config['SWIFT_KEY']
    authurl = current_app.config['SWIFT_AUTHURL']
    
    application = None
    data_process = "custom"
    processed_data_area_service = ["MongoDB"]
    other_data = other_meta
    #Search if the file is a zip or tar.gz
    if type_file == "application/x-zip-compressed" or type_file == "application/x-gzip" :
        #Split the file to retrieve the data
        df = file.split(",")
        df = df[1]
        #Decode the data
        df = base64.b64decode(df)
        #Creation of a temp file for stock the data
        fp = tempfile.TemporaryFile()
        fp.write(df)
        fp.seek(0)
        #Using ZipFile package to unzip zip file data
        zip = ZipFile(fp, 'r')
        #Using a for to read each file in the zip file
        for file in zip.filelist:
            #Read file to retrieve the data
            data_file = zip.read(file.filename)
            #Filename
            filename = file.filename
            #Split the filename to retrieve the extension file for the type file
            typef = file.filename.split('.')
            typef = typef[1]
            #Function return the type file
            type_file = typefile.typefile(typef)
            content_type = type_file
            file_content = data_file
            mongo.insert_datalake(file_content, user, key, authurl, container_name, filename,
                    processed_data_area_service, data_process, application,
                    content_type, mongodb_url, other_data)
    #Other type file   
    else:
        #Split the file to retrieve the data
        data_file = file.split(",")
        data_file = data_file[1]
        #Decode the data
        data_file = base64.b64decode(data_file)
        
        content_type = type_file
        file_content = data_file
        
        mongo.insert_datalake(file_content, user, key, authurl, container_name, filename,
                            processed_data_area_service, data_process, application,
                            content_type, mongodb_url, other_data)

    return jsonify({"response": "Done !"})
