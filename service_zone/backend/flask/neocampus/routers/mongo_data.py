from flask import Blueprint, jsonify, request, send_file
from ..services import mongo, influxdb
from datetime import datetime
import json, io, zipfile, time
import pandas as pd

mongo_data_bp = Blueprint('mongo_data_bp', __name__)


@mongo_data_bp.route('/raw-data', methods=['POST'])
def get_metadata():
    try:
        params = {
            'filetype': request.get_json()['filetype'],
            'datatype': request.get_json()['datatype'],
            'beginDate': request.get_json()['beginDate'],
            'endDate': request.get_json()['endDate']
        }
    except:
        return jsonify({'error': 'Missing required fields.'})

    if(("limit" in request.get_json() and "offset" not in request.get_json()) or ("limit" not in request.get_json() and "offset" in request.get_json())):
        return jsonify({'error': 'Limit and offset have to be sent together.'})

    if("limit" in request.get_json() and "offset" in request.get_json()):
        params['limit'] =  request.get_json()['limit']
        params['offset'] =  request.get_json()['offset']

    date_format = "%Y-%m-%d"

    try:
        convertedBeginDate = datetime.strptime(params['beginDate'], date_format)
        convertedEndDate = datetime.strptime(params['endDate'], date_format)
    except Exception as e:
        return jsonify({'error': str(e)})

    if(convertedBeginDate > convertedEndDate):
        params['beginDate'] = params['beginDate'] + " 23:59:59"
        params['endDate'] = params['endDate'] + " 00:00:00"
        date_format = "%Y-%m-%d %H:%M:%S"

        convertedBeginDateTemp = datetime.strptime(params['beginDate'], date_format)
        convertedBeginDate = datetime.strptime(params['endDate'], date_format)
        convertedEndDate = convertedBeginDateTemp

    if(convertedBeginDate == convertedEndDate):
        params['beginDate'] = params['beginDate'] + " 00:00:00"
        params['endDate'] = params['endDate'] + " 23:59:59"
        date_format = "%Y-%m-%d %H:%M:%S"

        convertedBeginDate = datetime.strptime(params['beginDate'], date_format)
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

    '''try:
        params = {
            'datatype': request.get_json()['datatype'],
            'beginDate': request.get_json()['beginDate'],
            'endDate': request.get_json()['endDate']
        }
    except:
        return jsonify({'error': 'Missing required fields.'})'''



    result = {}

    influxDB = influxdb.get_handled_data()
    mongoDB = mongo.get_handled_data()

    import sys

    # If there is Influx data
    if influxDB:
        metadata_influx_file = {
            'filename': 'InfluxDB.csv',
            'filesize': sys.getsizeof(influxDB)
        }
        result['influxDB'] = metadata_influx_file

    # If there is Mongo data
    if mongoDB :
        metadata_mongo_file = {
            'filename': 'MongoDB.json',
            'filesize': sys.getsizeof(mongoDB)
        }
        result['MongoDB'] = metadata_mongo_file

    return jsonify(result)

@mongo_data_bp.route('/handled-data-file', methods=['POST'])
def get_handled_data_zipped_file():
    '''try:
        params = {
            'datatype': request.get_json()['datatype'],
            'beginDate': request.get_json()['beginDate'],
            'endDate': request.get_json()['endDate']
        }
    except:
        return jsonify({'error': 'Missing required fields.'})'''

    # Result
    result = {
        'MongoDB': {},
        'InfluxDB': {}
    }

    # If MongoDB file has been selected
    if 'mongodb_file' in request.get_json():
        if request.get_json()["mongodb_file"]:
            # MongoDB data
            result['MongoDB'] = mongo.get_handled_data()

    # If InfluxDB file has been selected
    if 'influxdb_file' in request.get_json():
        if request.get_json()["influxdb_file"]:
            # InfluxDB data
            result['InfluxDB'] = influxdb.get_handled_data()

    memory_file = io.BytesIO()
    with zipfile.ZipFile(memory_file, 'w') as zip_file:
        files = result

        # JSON FILE - MONGODB
        if(result['MongoDB']):
            data = zipfile.ZipInfo("MongoDB.json")
            # Datetime
            data.date_time = time.localtime(time.time())[:6]

            # Compression method
            data.compress_type = zipfile.ZIP_DEFLATED

            # Writing JSON file into zipped result
            zip_file.writestr(data, result["MongoDB"])

        # CSV FILE - INFLUXDB
        if(result['InfluxDB']):
            data = zipfile.ZipInfo("InfluxDB.csv")
            data.date_time = time.localtime(time.time())[:6]
            data.compress_type = zipfile.ZIP_DEFLATED 

            # Parsing CSV Reader from InfluxDB to Pandas DataFrame 
            # To make possible CSV Data zipped
            df = pd.DataFrame(result['InfluxDB'])
            csv_bytes = df.to_csv().encode('utf-8')

            # Writing CSV file into zipped result
            zip_file.writestr(data, csv_bytes)

    # Position cursor - Necessary to change cursor at the beginning of the file
    memory_file.seek(0)

    # Tests if zip_file in memory is not empty - ZipFile class puts 22 kilobytes by default in zipped memory file
    if memory_file.getbuffer().nbytes > 22:
        return send_file(
            memory_file, 
            attachment_filename='handled_data.zip', 
            as_attachment=True
        )
    else:
        return jsonify({'msg': "No content available."})