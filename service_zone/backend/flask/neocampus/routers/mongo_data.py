from flask import Blueprint, jsonify, request, send_file, escape, current_app
from ..services import mongo, influxdb, keystone
from datetime import datetime
import json
import io
import zipfile
import time
import pandas as pd
from ..utils.size_conversion import convert_unit, SIZE_UNIT
from pymongo import MongoClient
from bson.objectid import ObjectId

mongo_data_bp = Blueprint('mongo_data_bp', __name__)

@mongo_data_bp.route('/last-raw-data', methods=['POST'])
def get_last_raw_data():
    """
    ---
    post:
        requestBody:
            required: true
            content:
                application/json:
                    schema: InputSchema
        description: get last raw data
        responses:
            '200':
                description: call successful
        tags:
            - mongodb_router
    """
    try:
        token = request.get_json()['token']
    except:
        return jsonify({'error': 'Missing token'})

    if keystone.login_token(current_app.config['KEYSTONE_URL'], token) == False:
        return jsonify({'error': 'Wrong Token'})


    params = request.get_json()

    if(("limit" in request.get_json() and "offset" not in request.get_json()) or ("limit" not in request.get_json() and "offset" in request.get_json())):
        return jsonify({'error': 'Limit and offset have to be sent together.'})

    if("sort_field" in request.get_json() and "sort_value" in request.get_json()):
        params['sort_field'] = request.get_json()['sort_field']
        params['sort_value'] = request.get_json()['sort_value']
    container_name = request.get_json()['container_name']
    nb_objects, mongo_collections = mongo.get_last_metadata(container_name, params)
    mongo_collections = list(mongo_collections)

    output = {'objects': []}
    for obj in mongo_collections:
        if('other_data' in obj.keys()):
            output['objects'].append({
                'original_object_name': obj['original_object_name'],
                "swift_container": obj['swift_container'],
                "content_type": obj['content_type'],
                'swift_object_id': obj['swift_object_id'],
                'other_data': obj['other_data'],
                'swift_user': obj['swift_user'],
                'creation_date': obj['creation_date']
            })

    output['length'] = nb_objects

    return jsonify({'result': output})    


@mongo_data_bp.route('/raw-data', methods=['POST'])
def get_metadata():
    """
    ---
    post:
        requestBody:
            required: true
            content:
                application/json:
                    schema: InputSchema
        description: get raw data
        responses:
            '200':
                description: call successful
        tags:
            - mongodb_router
    """
    try:
        params = {
            'filetype': request.get_json()['filetype'],
            'beginDate': request.get_json()['beginDate'],
            'endDate': request.get_json()['endDate'],
            'token': request.get_json()['token']
        }
    except:
        return jsonify({'error': 'Missing required fields.'})

    if keystone.login_token(current_app.config['KEYSTONE_URL'], params['token']) == False:
        return jsonify({'error': 'Wrong Token'})

    if(params.get('filetype') == ""):
        return jsonify({'error': 'Missing required fields.'})

    if(("limit" in request.get_json() and "offset" not in request.get_json()) or ("limit" not in request.get_json() and "offset" in request.get_json())):
        return jsonify({'error': 'Limit and offset have to be sent together.'})

    if("sort_field" in request.get_json() and "sort_value" in request.get_json()):
        params['sort_field'] = request.get_json()['sort_field']
        params['sort_value'] = request.get_json()['sort_value']

    # Sort columns
    if("limit" in request.get_json() and "offset" in request.get_json()):
        params['limit'] = request.get_json()['limit']
        params['offset'] = request.get_json()['offset']

    date_format = "%Y-%m-%d"

    try:
        convertedBeginDate = datetime.strptime(
            params['beginDate'], date_format)
        convertedEndDate = datetime.strptime(params['endDate'], date_format)
    except Exception as e:
        return jsonify({'error': str(e)})

    if(convertedBeginDate > convertedEndDate):
        params['beginDate'] = params['beginDate'] + " 23:59:59"
        params['endDate'] = params['endDate'] + " 00:00:00"
        date_format = "%Y-%m-%d %H:%M:%S"

        convertedBeginDateTemp = datetime.strptime(
            params['beginDate'], date_format)
        convertedBeginDate = datetime.strptime(params['endDate'], date_format)
        convertedEndDate = convertedBeginDateTemp

    if(convertedBeginDate == convertedEndDate):
        params['beginDate'] = params['beginDate'] + " 00:00:00"
        params['endDate'] = params['endDate'] + " 23:59:59"
        date_format = "%Y-%m-%d %H:%M:%S"

        convertedBeginDate = datetime.strptime(
            params['beginDate'], date_format)
        convertedEndDate = datetime.strptime(params['endDate'], date_format)

    if(convertedBeginDate < convertedEndDate):
        params['beginDate'] = params['beginDate'] + " 00:00:00"
        params['endDate'] = params['endDate'] + " 23:59:59"
        date_format = "%Y-%m-%d %H:%M:%S"

        convertedBeginDate = datetime.strptime(
            params['beginDate'], date_format)
        convertedEndDate = datetime.strptime(params['endDate'], date_format)

    params['beginDate'] = convertedBeginDate
    params['endDate'] = convertedEndDate
    container_name = request.get_json()['container_name']
    nb_objects, mongo_collections = mongo.get_metadata(container_name, params)
    mongo_collections = list(mongo_collections)

    output = {'objects': []}
    for obj in mongo_collections:
        output['objects'].append({
            'original_object_name': obj['original_object_name'],
            "swift_container": obj['swift_container'],
            "content_type": obj['content_type'],
            'swift_object_id': obj['swift_object_id'],
            'other_data': obj['other_data'] if 'other_data' in obj else '',
            'swift_user': obj['swift_user'],
            'creation_date': obj['creation_date']
        })

    output['length'] = nb_objects

    return jsonify({'result': output})


@mongo_data_bp.route('/handled-data-list', methods=['POST'])
def get_handled_data_list():
    """
    ---
    post:
        requestBody:
            required: true
            content:
                application/json:
                    schema: InputSchema
        description: get handled data list
        responses:
            '200':
                description: call successful
        tags:
            - mongodb_router
    """
    result = {}

    try:
        params = {
            'container_name': request.get_json(force=True)['container_name'],
            'filetype': request.get_json(force=True)['filetype'],
            'beginDate': request.get_json(force=True)['beginDate'],
            'endDate': request.get_json(force=True)['endDate'],
            'token': request.get_json(force=True)['token']
        }
    except:
        return jsonify({'error': 'Missing required fields.'})

    if keystone.login_token(current_app.config['KEYSTONE_URL'], params['token']) == False:
        return jsonify({'error': 'Wrong Token'})

    # InfluxDB data
    result = {}

    # Get data from different databases (InfluxDB and MongoDB)
    influxDB = influxdb.get_handled_data(params)
    mongoDB, mongo_nb_results = mongo.get_handled_data(params)

    import sys
    # Parse InfluxDB response to Pandas DataFrame
    influxdb_result, number_of_rows_influxdb = influxdb.create_csv_file(
        influxDB)
    nb_lines_influxDB = len(list(influxDB))

    # If there is Influx data (> 1 because Header row is present at the first line in csv file) 
    # and filter related to time series is selected
    if number_of_rows_influxdb > 1 and params.get('filetype') == 'timeseries':
        metadata_influx_file = {
            'filename': 'donnees-serie-temporelle-influxdb.csv',
            'filesize': sys.getsizeof(influxdb_result)
        }
        result['influxDB'] = metadata_influx_file

    # If there is Mongo data and filter "Images" or "Time series" are selected
    if mongo_nb_results > 0 and params.get('filetype') == 'metadata':
        metadata_mongo_file = {
            'filename': 'metadonnees-images-mongodb.json',
            'filesize': sys.getsizeof(mongoDB)
        }
        result['MongoDB'] = metadata_mongo_file

    return jsonify(result)


@mongo_data_bp.route('/handled-data-file', methods=['POST'])
def get_handled_data_zipped_file():
    """
    ---
    post:
        requestBody:
            required: true
            content:
                application/json:
                    schema: InputSchema
        description: get handled data file
        responses:
            '200':
                description: call successful
        tags:
            - mongodb_router
    """
    data_request = request.get_json(force=True)[0]

    try:
        params = {
            'container_name': data_request['container_name'],
            'filetype': data_request['filetype'],
            'beginDate': data_request['beginDate'],
            'endDate': data_request['endDate'],
            'token': data_request['token']
        }
    except:
        return jsonify({'error': 'Missing required fields.'})

    if keystone.login_token(current_app.config['KEYSTONE_URL'], params['token']) == False:
        return jsonify({'error': 'Wrong Token'})
    # Result
    result = {
        'MongoDB': {},
        'InfluxDB': {}
    }

    mongo_nb_results = 0
    number_of_rows_influxdb = 0

    # If MongoDB file has been selected
    if 'mongodb_file' in data_request:
        if data_request["mongodb_file"]:
            # MongoDB data
            mongodb_result, mongo_nb_results = mongo.get_handled_data(params)
            result['MongoDB'] = mongodb_result

    # If InfluxDB file has been selected
    if 'influxdb_file' in data_request:
        if data_request["influxdb_file"]:
            # InfluxDB data
            result['InfluxDB'] = influxdb.get_handled_data(params)

            # Parse InfluxDB response to Pandas DataFrame
            influxdb_result, number_of_rows_influxdb = influxdb.create_csv_file(
                result['InfluxDB'])

    memory_file = io.BytesIO()
    with zipfile.ZipFile(memory_file, 'w') as zip_file:
        files = result

        # JSON FILE - MONGODB
        if(mongo_nb_results > 0):
            data = zipfile.ZipInfo("metadonnees-images-mongodb.json")
            # Datetime
            data.date_time = time.localtime(time.time())[:6]

            # Compression method
            data.compress_type = zipfile.ZIP_DEFLATED

            # Writing JSON file into zipped result
            zip_file.writestr(data, result["MongoDB"])

        # CSV FILE - INFLUXDB
        if(number_of_rows_influxdb > 1):
            data = zipfile.ZipInfo("donnees-serie-temporelle-influxdb.csv")
            data.date_time = time.localtime(time.time())[:6]
            data.compress_type = zipfile.ZIP_DEFLATED

            # Writing CSV file into zipped result
            zip_file.writestr(data, influxdb_result)

    # Position cursor - Necessary to change cursor at the beginning of the file
    memory_file.seek(0)

    if memory_file.getbuffer().nbytes > 22:
        return send_file(
            memory_file,
            attachment_filename='handled_data.zip',
            as_attachment=True
        )
    else:
        return jsonify({'msg': "No content available."})

@mongo_data_bp.route('/models/all', methods=['GET', 'POST'])
def get_models():
    """
    ---
    post:
        requestBody:
            required: true
            content:
                application/json:
                    schema: InputSchema
        description: get all models
        responses:
            '200':
                description: call successful
        tags:
            - mongodb_router
    """
    try:
        token = request.get_json()['token']
    except:
        return jsonify({'error': 'Missing token'})

    if keystone.login_token(current_app.config['KEYSTONE_URL'], token) == False:
        return jsonify({'error': 'Wrong Token'})

    container_name = request.get_json()['container_name']
    models = mongo.get_models_all(container_name)
    models_list = list(models)

    output = {'data': []}
    for obj in models_list:
        output['data'].append({
            '_id': str(obj['_id']),
            "label": obj['label'],
            "type_file_accepted": obj['type_file_accepted'],
            "metadonnees": obj['metadonnees'],
            "status": obj['status'],
        })
        
    return jsonify({'models': output})

@mongo_data_bp.route('/models/show/all', methods=['GET', 'POST'])
def get_models_show():
    """
    ---
    post:
        requestBody:
            required: true
            content:
                application/json:
                    schema: InputSchema
        description: get models with status true
        responses:
            '200':
                description: call successful
        tags:
            - mongodb_router
    """

    try:
            token = request.get_json()['token']
    except:
        return jsonify({'error': 'Missing token'})

    if keystone.login_token(current_app.config['KEYSTONE_URL'], token) == False:
        return jsonify({'error': 'Wrong Token'})

    container_name = request.get_json()['container_name']
    models = mongo.get_models_show_all(container_name)
    models_list = list(models)

    output = {'data': []}
    for obj in models_list:
        output['data'].append({
            '_id': str(obj['_id']),
            "label": obj['label'],
            "type_file_accepted": obj['type_file_accepted'],
            "metadonnees": obj['metadonnees'],
            "status": obj['status'],
        })
        
    return jsonify({'models': output})

@mongo_data_bp.route('/models/cache/all', methods=['GET', 'POST'])
def get_models_cache():
    """
    ---
    post:
        requestBody:
            required: true
            content:
                application/json:
                    schema: InputSchema
        description:  get models with status false
        responses:
            '200':
                description: call successful
        tags:
            - mongodb_router
    """
    try:
        token = request.get_json()['token']
    except:
        return jsonify({'error': 'Missing token'})

    if keystone.login_token(current_app.config['KEYSTONE_URL'], token) == False:
        return jsonify({'error': 'Wrong Token'})

    container_name = request.get_json()['container_name']
    models = mongo.get_models_all_cache(container_name)
    models_list = list(models)
    #Data formatting for output
    output = {'data': []}
    for obj in models_list:
        output['data'].append({
            '_id': str(obj['_id']),
            "label": obj['label'],
            "type_file_accepted": obj['type_file_accepted'],
            "metadonnees": obj['metadonnees'],
            "status": obj['status'],
        })
        
    return jsonify({'models': output})


@mongo_data_bp.route('/models/params', methods=['GET', 'POST'])
def get_models_params():
    """
    ---
    post:
        requestBody:
            required: true
            content:
                application/json:
                    schema: InputSchema
        description:  get models with params
        responses:
            '200':
                description: call successful
        tags:
            - mongodb_router
    """
    try:
        token = request.get_json()['token']
    except:
        return jsonify({'error': 'Missing token'})

    if keystone.login_token(current_app.config['KEYSTONE_URL'], token) == False:
        return jsonify({'error': 'Wrong Token'})
    data_request = request.get_json()
    types_files = data_request['types_files']
    models_list = []
    container_name = request.get_json()['container_name']
    #Recovery of all templates for each file type
    for type_file in types_files:
        models = mongo.get_models_params(type_file, container_name)
        models_list.append(models)
        
    #Liste des différents modèles sans doublon
    models_param = []
    for model in models_list:
        for m in model:
            if m not in models_param: models_param.append(m)
        
    #Data formatting for output
    listmodels = list(models_param)
    output = {'data': []}
    for obj in listmodels:
        output['data'].append({
            '_id': str(obj['_id']),
            "label": obj['label'],
            "type_file_accepted": obj['type_file_accepted'],
            "metadonnees": obj['metadonnees'],
        })
    return jsonify({'models': output})


@mongo_data_bp.route('/models/id', methods=['GET', 'POST'])
def get_model_id():
    """
    ---
    post:
        requestBody:
            required: true
            content:
                application/json:
                    schema: InputSchema
        description: get model
        responses:
            '200':
                description: call successful
        tags:
            - mongodb_router
    """
    try:
        token = request.get_json()['token']
    except:
        return jsonify({'error': 'Missing token'})

    if keystone.login_token(current_app.config['KEYSTONE_URL'], token) == False:
        return jsonify({'error': 'Wrong Token'})

    data_request = request.get_json()
    id = data_request['id']
    models = mongo.get_model_id(id)
    model = list(models)

    for obj in model:
        output = {
            '_id': str(obj['_id']),
            "label": obj['label'],
            "type_file_accepted": obj['type_file_accepted'],
            "metadonnees": obj['metadonnees'],
            "status": obj['status'],
        }
        
    return jsonify({'model': output})

@mongo_data_bp.route('/models/add', methods=['POST'])
def add_models():
    """
    ---
    get:
        description: edit model
        responses:
            '200':
                description: call successful
        tags:
            - mongodb_router
    """
    try:
        token = request.get_json()['token']
    except:
        return jsonify({'error': 'Missing token'})

    if keystone.login_token(current_app.config['KEYSTONE_URL'], token) == False:
        return jsonify({'error': 'Wrong Token'})

    data_request = request.get_json()
    param = {
        'label': data_request['label'],
        'type_file_accepted': data_request['type_file_accepted'],
        'metadonnees': data_request['metadonnees'],
        'status': data_request['status'],
        'container_name': data_request['container_name'],
    }
    model = mongo.add_model(param)

    return jsonify({'model': model})


@mongo_data_bp.route('/models/edit', methods=['POST'])
def edit_models():
    """
    ---
    get:
        description: edit model
        responses:
            '200':
                description: call successful
        tags:
            - mongodb_router
    """
    try:
        token = request.get_json()['token']
    except:
        return jsonify({'error': 'Missing token'})

    if keystone.login_token(current_app.config['KEYSTONE_URL'], token) == False:
        return jsonify({'error': 'Wrong Token'})

    data_request = request.get_json()
    param = {
        'id': data_request['id'],
        'label': data_request['label'],
        'type_file_accepted': data_request['type_file_accepted'],
        'metadonnees': data_request['metadonnees'],
        'status': data_request['status'],
        'container_name': data_request['container_name'],
    }
    model = mongo.update_model(param)

    return jsonify({'model': model})

@mongo_data_bp.route('/getDataAnomaly', methods=['GET','POST'])
def get_anomalies():
    """
    ---
    get:
        description:  get anomalies from influx db to mongodb 
        responses:
            '200':
                description: call successful
        tags:
            - mongodb_router
    """
    try:
            token = request.get_json()['token']
    except:
        return jsonify({'error': 'Missing token'})

    if keystone.login_token(current_app.config['KEYSTONE_URL'], token) == False:
        return jsonify({'error': 'Wrong Token'})

    container_name = request.get_json()['container_name']
    measurement = request.get_json()["measurement"]
    topic = request.get_json()["topic"]
    
    start = request.get_json()["startDate"]
    end = request.get_json()["endDate"]
    try:
        params = {
            'beginDate' : start + "T00:00:00.000000Z",
            'endDate' : end + "T23:59:59.000000Z"}
    except:
        return jsonify({'error': 'Missing required fields.'})

    mongo_collections = mongo.get_anomaly(params,measurement,topic, container_name)
    mongo_collections = list(mongo_collections)

    output = {'objects': []}
    for obj in mongo_collections:
        output['objects'].append({
            '_id': str(obj['_id']),
            "topic": obj['topic'],
            "value": obj['value'],
            "unit": obj['unit'],
            'datetime': obj['datetime'],
            'endDate_detection': obj['endDate_detection'],
            'startDate_detection': obj['startDate_detection']
        })

    return jsonify({'anomly': output})

@mongo_data_bp.route('/getDataAnomalyAll', methods=['GET', 'POST'])
def get_anomalies_all():
    """
    ---
    get:
        description: insert_anomaly from influx db to mongodb 
        responses:
            '200':
                description: call successful
        tags:
            - mongodb_router
    """
    try:
        token = request.get_json()['token']
    except:
        return jsonify({'error': 'Missing token'})

    if keystone.login_token(current_app.config['KEYSTONE_URL'], token) == False:
        return jsonify({'error': 'Wrong Token'})

    container_name = request.get_json()['container_name']
    nbr_metadata, metadata = mongo.get_anomaly_all(container_name)

    mongo_collections = list(metadata)
    output = {'objects': []}
    for obj in mongo_collections:
        output['objects'].append({
            '_id': str(obj['_id']),
            "topic": obj['topic'],
            "value": obj['value'],
            "unit": obj['unit'],
            'datetime': obj['datetime'],
            'endDate_detection': obj['endDate_detection'],
            'startDate_detection': obj['startDate_detection']
        })
    output['length'] = nbr_metadata
    
    return jsonify({'anomaly': output})

@mongo_data_bp.route('/countDataAnomalyAll', methods=['GET', 'POST'])
def count_anomalies_all():
    """
    ---
    get:
        description: get anomaly amount
        responses:
            '200':
                description: call successful
        tags:
            - mongodb_router
    """
    try:
        token = request.get_json()['token']
    except:
        return jsonify({'error': 'Missing token'})

    if keystone.login_token(current_app.config['KEYSTONE_URL'], token) == False:
        return jsonify({'error': 'Wrong Token'})

    mongodb_url = current_app.config['MONGO_URL']
    collection = MongoClient(mongodb_url, connect=False).data_anomaly.influxdb_anomaly
    container_name = request.get_json()['container_name']
    print(container_name)
    metadata = collection.find({'container_name': container_name})
    nbrAnomaly = str(metadata.count())

    #output = {"msg": "I'm the test endpoint from blueprint_x."}
    #return jsonify(output)

    return nbrAnomaly


@mongo_data_bp.route('/uploadssh', methods=['GET', 'POST'])
def list_upload_ssh():
    """
    ---
    get:
        description: get all upload large file no finished upload process
        responses:
            '200':
                description: call successful
        tags:
        - mongodb_router

    """
    try:
        token = request.get_json()['token']
    except:
        return jsonify({'error': 'Missing token'})

    if keystone.login_token(current_app.config['KEYSTONE_URL'], token) == False:
        return jsonify({'error': 'Wrong Token'})

    container_name = request.get_json()['container_name']
    mongodb_url = current_app.config['MONGO_URL']
    mongo_client = MongoClient(mongodb_url, connect=False)
    mongo_db = mongo_client.upload
    collection = mongo_db["file_upload"]
    
    files_upload = collection.find({'container_name': container_name},{ "_id": 0})
    files_upload_list = list(files_upload)
    return jsonify({'file_upload': files_upload_list})

@mongo_data_bp.route('/mqtt/add', methods=['POST'])
def create_mqtt_flux():
    """
    ---
    get:
        description: Create config of a flux mqtt
        responses:
            '200':
                description: call successful
        tags:
        - mongodb_router

    """
    try:
        params = {
            "name": request.get_json()['name'],
            "description": request.get_json()['description'],
            "brokerUrl": request.get_json()['brokerUrl'],
            "user": request.get_json()['user'],
            "password": request.get_json()['password'],
            "topic": request.get_json()['topic'],
            "container_name": request.get_json()['container_name'],
            "status": request.get_json()['status'],
            "token": request.get_json()['token']
        }
    except:
        return jsonify({'error': 'Missing required fields.'})

    if keystone.login_token(current_app.config['KEYSTONE_URL'], params['token']) == False:
        return jsonify({'error': 'Wrong Token'})

    flux = {
        "name": params['name'],
        "description": params['description'],
        "brokerUrl": params['brokerUrl'],
        "user": params['user'],
        "password": params['password'],
        "topic": params['topic'],
        "container_name": params['container_name'],
        "status": params['status']
    }
    mongodb_url = current_app.config['MONGO_URL']
    mongo_client = MongoClient(mongodb_url, connect=False)
    mongo_db = mongo_client.mqtt
    collection = mongo_db["flux"]
    collection.insert_one(flux)
    return jsonify({'Result': "Done"})

@mongo_data_bp.route('/mqtt/edit', methods=['POST'])
def edit_mqtt_flux():
    """
    ---
    get:
        description: Edit config of a flux mqtt
        responses:
            '200':
                description: call successful
        tags:
        - mongodb_router

    """
    try:
        params = {
            "id": request.get_json()['id'],
            "name": request.get_json()['name'],
            "description": request.get_json()['description'],
            "brokerUrl": request.get_json()['brokerUrl'],
            "user": request.get_json()['user'],
            "password": request.get_json()['password'],
            "topic": request.get_json()['topic'],
            "container_name": request.get_json()['container_name'],
            "status": request.get_json()['status'],
            "token": request.get_json()['token']
        }
    except:
        return jsonify({'error': 'Missing required fields.'})

    if keystone.login_token(current_app.config['KEYSTONE_URL'], params['token']) == False:
        return jsonify({'error': 'Wrong Token'})

    query = {"_id": ObjectId(params['id'])}
    update_values = {"$set": {
        "name": params['name'],
        "description": params['description'],
        "brokerUrl": params['brokerUrl'],
        "user": params['user'],
        "password": params['password'],
        "topic": params['topic'],
        "container_name": params['container_name'],
        "status": params['status']
    }}

    mongodb_url = current_app.config['MONGO_URL']
    mongo_client = MongoClient(mongodb_url, connect=False)
    mongo_db = mongo_client.mqtt
    collection = mongo_db["flux"]
    collection.update_one(query, update_values, upsert=False)
    return jsonify({'Result': "Done"})

@mongo_data_bp.route('/mqtt/status/change', methods=['POST'])
def change_status_mqtt_flux():
    """
    ---
    get:
        description: Change status of config flux mqtt
        responses:
            '200':
                description: call successful
        tags:
        - mongodb_router

    """
    try:
        params = {
            "id": request.get_json()['id'],
            "status": request.get_json()['status'],
            "token": request.get_json()['token']
        }
    except:
        return jsonify({'error': 'Missing required fields.'})

    if keystone.login_token(current_app.config['KEYSTONE_URL'], params['token']) == False:
        return jsonify({'error': 'Wrong Token'})

    query = {"_id": ObjectId(params['id'])}
    status_change = { "$set": { "status": params['status'] } }

    mongodb_url = current_app.config['MONGO_URL']
    mongo_client = MongoClient(mongodb_url, connect=False)
    mongo_db = mongo_client.mqtt
    collection = mongo_db["flux"]
    collection.update_one(query, status_change, upsert=False)
    return jsonify({'Result': "Done"})

@mongo_data_bp.route('/mqtt/all', methods=['GET', 'POST'])
def show_mqtt_flux():
    """
    ---
    get:
        description: Change status of config flux mqtt
        responses:
            '200':
                description: call successful
        tags:
        - mongodb_router

    """
    try:
        params = {
            "container_name": request.get_json()['container_name'],
            "token": request.get_json()['token'],
        }
    except:
        return jsonify({'error': 'Missing required fields.'})

    if keystone.login_token(current_app.config['KEYSTONE_URL'], params['token']) == False:
        return jsonify({'error': 'Wrong Token'})

    container_name = params['container_name']
    mongodb_url = current_app.config['MONGO_URL']
    mongo_client = MongoClient(mongodb_url, connect=False)
    mongo_db = mongo_client.mqtt
    collection = mongo_db["flux"]

    flux = collection.find({'container_name': container_name})
    list_flux = list(flux)
    output = {'data': []}
    for obj in list_flux:
        output['data'].append({
            '_id': str(obj['_id']),
            "name": obj['name'],
            "description": obj['description'],
            "brokerUrl": obj['brokerUrl'],
            "user": obj['user'],
            "password": obj['password'],
            "topic": obj['topic'],
            "container_name": obj['container_name'],
            "status": obj['status']
        })
    return jsonify({'list_flux': output})

@mongo_data_bp.route('/mqtt/status/actif', methods=['GET', 'POST'])
def show_mqtt_flux_actifs():
    """
    ---
    get:
        description: Change status of config flux mqtt actifs
        responses:
            '200':
                description: call successful
        tags:
        - mongodb_router

    """
    try:
        params = {
            "container_name": request.get_json()['container_name'],
            "token": request.get_json()['token'],
        }
    except:
        return jsonify({'error': 'Missing required fields.'})

    if keystone.login_token(current_app.config['KEYSTONE_URL'], params['token']) == False:
        return jsonify({'error': 'Wrong Token'})

    container_name = params['container_name']
    mongodb_url = current_app.config['MONGO_URL']
    mongo_client = MongoClient(mongodb_url, connect=False)
    mongo_db = mongo_client.mqtt
    collection = mongo_db["flux"]

    flux = collection.find({'container_name': container_name, 'status': True})
    list_flux = list(flux)
    output = {'data': []}
    for obj in list_flux:
        output['data'].append({
            '_id': str(obj['_id']),
            "name": obj['name'],
            "description": obj['description'],
            "brokerUrl": obj['brokerUrl'],
            "user": obj['user'],
            "password": obj['password'],
            "topic": obj['topic'],
            "container_name": obj['container_name'],
            "status": obj['status']
        })
    return jsonify({'list_flux': output})