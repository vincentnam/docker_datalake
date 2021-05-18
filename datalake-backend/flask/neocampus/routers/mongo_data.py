from flask import Blueprint, jsonify, request
from ..services import mongo
from flask_cors import cross_origin
from datetime import datetime

mongo_data_bp = Blueprint('mongo_data_bp', __name__)


@mongo_data_bp.route('/raw-data', methods=['POST'])
@cross_origin(supports_credentials=True)
def get_metadata():
    params = {
        'limit': request.get_json()['limit'],
        'offset': request.get_json()['offset'],
        'filetype': request.get_json()['filetype'],
        'beginDate': request.get_json()['beginDate'],
        'endDate': request.get_json()['endDate']
    }

    date_format = "%Y-%m-%d"

    params['beginDate'] = datetime.strptime(params['beginDate'], date_format)
    params['endDate'] = datetime.strptime(params['endDate'], date_format)

    nb_objects, mongo_collections = mongo.get_metadata("neOCampus", params)
    mongo_collections = list(mongo_collections)

    output = {'objects': []}
    for obj in mongo_collections:
        output['objects'].append({
            'original_object_name': obj['original_object_name'],
            "swift_container": obj['swift_container'],
            "content_type": obj['content_type'],
            'swift_object_id': obj['swift_object_id'],
            'swift_user': obj['swift_user'],
            'creation_date': obj['creation_date']
        })

    output['length'] = nb_objects

    return jsonify({'result': output})
