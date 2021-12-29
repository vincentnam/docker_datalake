from flask import Blueprint, jsonify, request, send_file, escape, current_app
from ..services import mongo, influxdb
from datetime import datetime
import json
import io
import zipfile
import time
import pandas as pd
from ..utils.size_conversion import convert_unit, SIZE_UNIT
from pymongo import MongoClient
import datetime

mongo_data_bp = Blueprint('mongo_data_bp', __name__)

@mongo_data_bp.route('/last-raw-data', methods=['POST'])
def get_last_raw_data():
    params = request.get_json()

    if(("limit" in request.get_json() and "offset" not in request.get_json()) or ("limit" not in request.get_json() and "offset" in request.get_json())):
        return jsonify({'error': 'Limit and offset have to be sent together.'})

    if("sort_field" in request.get_json() and "sort_value" in request.get_json()):
        params['sort_field'] = request.get_json()['sort_field']
        params['sort_value'] = request.get_json()['sort_value']

    nb_objects, mongo_collections = mongo.get_last_metadata("neOCampus", params)
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
    try:
        params = {
            'filetype': request.get_json()['filetype'],
            'beginDate': request.get_json()['beginDate'],
            'endDate': request.get_json()['endDate']
        }
    except:
        return jsonify({'error': 'Missing required fields.'})

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

    nb_objects, mongo_collections = mongo.get_metadata("neOCampus", params)
    mongo_collections = list(mongo_collections)

    output = {'objects': []}
    for obj in mongo_collections:
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


@mongo_data_bp.route('/handled-data-list', methods=['POST'])
def get_handled_data_list():
    result = {}

    try:
        params = {
            'filetype': request.get_json(force=True)['filetype'],
            'beginDate': request.get_json(force=True)['beginDate'],
            'endDate': request.get_json(force=True)['endDate']
        }
    except:
        return jsonify({'error': 'Missing required fields.'})

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

    # If there is Influx data (> 1 because Header is present at minimum in csv file) and filter "Time series" is selected
    if number_of_rows_influxdb > 1 and "csv" in params.get('filetype'):
        metadata_influx_file = {
            'filename': 'donnees-serie-temporelle-influxdb.csv',
            'filesize': sys.getsizeof(influxdb_result)
        }
        result['influxDB'] = metadata_influx_file

    # If there is Mongo data and filter "Images" or "Time series" are selected
    if mongo_nb_results > 0 and "image" in params.get('filetype'):
        metadata_mongo_file = {
            'filename': 'metadonnees-images-mongodb.json',
            'filesize': sys.getsizeof(mongoDB)
        }
        result['MongoDB'] = metadata_mongo_file

    return jsonify(result)


@mongo_data_bp.route('/handled-data-file', methods=['POST'])
def get_handled_data_zipped_file():
    data_request = request.get_json(force=True)[0]

    try:
        params = {
            'filetype': data_request['filetype'],
            'beginDate': data_request['beginDate'],
            'endDate': data_request['endDate']
        }
    except:
        return jsonify({'error': 'Missing required fields.'})

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

@mongo_data_bp.route('/models/all', methods=['GET'])
def get_models():
    models = mongo.get_models_all()
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

@mongo_data_bp.route('/models/show/all', methods=['GET'])
def get_models_show():
    models = mongo.get_models_show_all()
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

@mongo_data_bp.route('/models/cache/all', methods=['GET'])
def get_models_cache():
    models = mongo.get_models_all_cache()
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
    data_request = request.get_json()
    types_files = data_request['types_files']
    models_list = []
    #Recovery of all templates for each file type
    for type_file in types_files:
        models = mongo.get_models_params(type_file)
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
    data_request = request.get_json()
    id = data_request['id']
    models = mongo.get_model_id(id)
    model = list(models)

    output = {'data': []}
    for obj in model:
        output['data'].append({
            '_id': str(obj['_id']),
            "label": obj['label'],
            "type_file_accepted": obj['type_file_accepted'],
            "metadonnees": obj['metadonnees'],
            "status": obj['status'],
        })
        
    return jsonify({'model': output})

@mongo_data_bp.route('/models/add', methods=['POST'])
def add_models():
    data_request = request.get_json()
    param = {
        'label': data_request['label'],
        'type_file_accepted': data_request['type_file_accepted'],
        'metadonnees': data_request['metadonnees'],
        'status': data_request['status'],
    }
    model = mongo.add_model(param)

    return jsonify({'model': model})


@mongo_data_bp.route('/models/edit', methods=['POST'])
def edit_models():
    data_request = request.get_json()
    param = {
        'id': data_request['id'],
        'label': data_request['label'],
        'type_file_accepted': data_request['type_file_accepted'],
        'metadonnees': data_request['metadonnees'],
        'status': data_request['status']
    }
    model = mongo.update_model(param)

    return jsonify({'model': model})

@mongo_data_bp.route('/getDataAnomaly', methods=['GET','POST'])
def get_anomalies():
    """
    insert_anomaly from influx db to mongodb 
    :param anomaly:
    :param mongodb_url:
    :return: done
    """
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

    x = influxdb.get_data_anomaly(50, 150)
    print("insert")    
    print(params['beginDate'])
    print(params['endDate'])

    mongo_collections = mongo.get_anomaly(params,measurement,topic)
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

@mongo_data_bp.route('/getDataAnomalyAll', methods=['GET'])
def get_anomalies_all():
    """
    insert_anomaly from influx db to mongodb 
    :param anomaly:
    :param mongodb_url:
    :return: done
    """
    
    nbr_metadata, metadata = mongo.get_anomaly_all()

    mongo_collections = list(metadata)
    print('all anomaly')
    print(metadata)
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

@mongo_data_bp.route('/countDataAnomalyAll', methods=['GET'])
def count_anomalies_all():
    """
    insert_anomaly from influx db to mongodb 
    :param anomaly:
    :param mongodb_url:
    :return: done
    """
    mongodb_url = current_app.config['MONGO_URL']
    collection = MongoClient(mongodb_url, connect=False).data_anomaly.influxdb_anomaly

    metadata = collection.find()
    nbrAnomaly = str(metadata.count())
    return nbrAnomaly
