import os
import uuid
from zipfile import ZipFile
import base64
import json
from flask import Blueprint, jsonify, current_app, request, send_from_directory, make_response
from ..services import swift, mongo, keystone
import os
from multiprocessing import Process
from pymongo import MongoClient
import swiftclient
import datetime

swift_file_bp = Blueprint('swift_file_bp', __name__)


@swift_file_bp.route('/swift-files', methods=['POST'])
def swift_files():
    """
    ---
    post:
        requestBody:
            required: true
            content:
                application/json:
                    schema: InputSchema
        description: get Openstack Swift files
        responses:
            '200':
                description: call successful
        tags:
            - openstack_swift_router
    """
    request_result = request.get_json()[0]
    try:
        token = request_result['token']
    except:
        return jsonify({'error': 'Missing token'})

    if keystone.login_token(current_app.config['KEYSTONE_URL'], token) == False:
        return jsonify({'error': 'Wrong Token'})

    swift_files = []
    zip_file_name = f'{str(uuid.uuid4().hex)}.zip'
    zip_path = os.path.join(
        current_app.config['SWIFT_FILES_DIRECTORY'], zip_file_name)
    zip_obj = ZipFile(os.path.join(current_app.root_path, zip_path), 'w')

    for co in request.get_json():
        container_name = co["container_name"]
        object_id = co["object_id"]
        file_path = swift.download_object_file(container_name, object_id)
        swift_files.append({
            "container_name": container_name,
            "object_id": object_id,
            "object_file": os.path.join(current_app.config['HOST_URL'], file_path)
        })
        zip_obj.write(os.path.join(current_app.root_path,
                      file_path), os.path.basename(file_path))
    zip_obj.close()

    result = {
        'swift_files': swift_files,
        'swift_zip': os.path.join(current_app.config['HOST_URL'], 'api', zip_path),
    }
    return jsonify(result)


@swift_file_bp.route('/cache-swift-files/<path:filename>')
def download(filename):
    """
    ---
    get:
        parameters:
            - in: query
              name: path
              schema:
                type: string
            - in: query
              name: filename
              schema:
                type: string
        description: download file
        responses:
            '200':
                description: call successful
        tags:
            - openstack_swift_router
    """
    swift_files_directory = os.path.join(
        current_app.root_path, current_app.config['SWIFT_FILES_DIRECTORY'])
    return send_from_directory(directory=swift_files_directory, filename=filename)

@swift_file_bp.route('/storage', methods=['POST'])
def storage():
    """
    ---
    post:
        requestBody:
            required: true
            content:
                application/json:
                    schema: InputSchema
        description: Upload file
        responses:
            '200':
                description: call successful
        tags:
            - openstack_swift_router
    """
    try:
        token = request.get_json()['token']
    except:
        return jsonify({'error': 'Missing token'})

    if keystone.login_token(current_app.config['KEYSTONE_URL'], token) == False:
        return jsonify({'error': 'Wrong Token'})

    file = request.get_json()["file"]
    filename = request.get_json()["filename"]
    other_meta = request.get_json()["othermeta"]
    type_file = request.get_json()["typeFile"]
    link_file = request.get_json()["linkFile"]
    link_type = request.get_json()["linkType"]
    container_name = request.get_json()["container_name"]

    if link_file != "":

        user = current_app.config['USER']
        password = current_app.config['PASSWORD']
        path = ""
        link = link_file.split('/')
        if link_type == "ip":
            link_ssh = link[0]
            path = "/" + "/".join(link[1:])
        else:
            link_ssh = link[2]
            path = "/" + "/".join(link[3:])

        filename = path.split("/")[-1]

        upload_processing = Process(target=swift.ssh_file, name="Upload_ssh", args=(
            link_ssh,
            user,
            password,
            path,
            filename,
            type_file,
            container_name,
            other_meta
        ))
        upload_processing.start()

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

@swift_file_bp.route('/upload-big-file', methods=['POST'])
def upload():
    """
    ---
    post:
        requestBody:
            required: true
            content:
                application/json:
                    schema: InputSchema
        description: Upload big file
        responses:
            '200':
                description: call successful
        tags:
            - openstack_swift_router
    """
    file = request.files['file']

    #Traçability file upload
    mongodb_url = current_app.config['MONGO_URL']
    mongo_client = MongoClient(mongodb_url, username=current_app.config['MONGO_ADMIN'], password=current_app.config['MONGO_PWD'], authSource=current_app.config['MONGO_DB_AUTH'], connect=False)
    mongo_db = mongo_client.upload
    mongo_collection = mongo_db["file_upload"]

    save_path = os.path.join(
        current_app.root_path, current_app.config['SWIFT_FILES_DIRECTORY'], file.filename)
    current_chunk = int(request.form['dzchunkindex'])

    # If the file already exists it's ok if we are appending to it,
    # but not if it's new file that would overwrite the existing one
    if os.path.exists(save_path) and current_chunk == 0:
        # 400 and 500s will tell dropzone that an error occurred and show an error
        return make_response(('File already exists', 400))

    try:
        with open(save_path, 'ab') as f:
            f.seek(int(request.form['dzchunkbyteoffset']))
            f.write(file.stream.read())
    except OSError:
        # log.exception will include the traceback so we can see what's wrong
        return make_response(("Not sure why,"
                              " but we couldn't write the file to disk", 500))

    total_chunks = int(request.form['dztotalchunkcount'])


    if current_chunk == 0:
        new_value = True
        if new_value == True:
            extension = file.filename.split(".")
            extension = extension.pop()
            type_file = mongo.typefile(extension)
            data = {
                "filename": file.filename,
                "type_file": type_file,
                "total_bytes_download": os.path.getsize(save_path),
                "total_bytes": request.form['dztotalfilesize'],
                "created_at": datetime.datetime.now(),
                "update_at": datetime.datetime.now(),
                "container_name": request.form["container_name"],
                "upload_swift": False,
                "id_big_file": request.form["id_big_file"]
            }
            id_file_upload = mongo_collection.insert_one(data).inserted_id
            new_value = False
    else:
        doc = {"id_big_file": request.form["id_big_file"]}
        newvalues = { "$set": { "total_bytes_download": os.path.getsize(save_path), "update_at": datetime.datetime.now() } }
        mongo_collection.update_one(doc, newvalues)

    if current_chunk + 1 == total_chunks:
        doc = {"id_big_file": request.form["id_big_file"]}
        newvalues = { "$set": { "total_bytes_download": request.form['dztotalfilesize'], "update_at": datetime.datetime.now() } }
        mongo_collection.update_one(doc, newvalues)
        # This was the last chunk, the file should be complete and the size we expect
        if os.path.getsize(save_path) != int(request.form['dztotalfilesize']):
            return make_response(('Size mismatch', 500))
        else:
            other_data = json.loads(request.form["othermeta"])
            extension = file.filename.split(".")
            extension = extension.pop()
            type_file = mongo.typefile(extension)

            container_name = request.form["container_name"]
            filename = file.filename

            # Get content file totally
            filepath = os.path.join(
            current_app.root_path,
            current_app.config['SWIFT_FILES_DIRECTORY'],
            file.filename
            )

            file = open(filepath, 'rb')
            data_file = swift.read_in_chunks(file)

            file_content = data_file
            mongodb_url = current_app.config['MONGO_URL']
            user = current_app.config['SWIFT_USER']
            key = current_app.config['SWIFT_KEY']
            authurl = current_app.config['SWIFT_AUTHURL']
            content_type = type_file
            application = None
            data_process = "custom"
            processed_data_area_service = ["MongoDB"]
            id_big_file = request.form["id_big_file"]

            # Multithreading for upload file from backend to Openstack Swift in background
            upload_processing = Process(
                target=mongo.insert_datalake,
                name="Upload_Openstack_Swift",
                args=(
                    file_content, user, key, authurl,
                    container_name, filename, processed_data_area_service, data_process,
                    application, content_type, mongodb_url, other_data, id_big_file
                )
            )
            upload_processing.start()

    return make_response(("Chunk upload successful", 200))
