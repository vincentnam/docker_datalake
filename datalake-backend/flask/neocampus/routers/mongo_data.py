from flask import Blueprint, jsonify, request
from ..services import mongo

mongo_data_bp = Blueprint('mongo_data_bp', __name__)


@mongo_data_bp.route('/raw-data')
def get_metadata():
    limit = request.args.get('limit', type=int)
    offset = request.args.get('offset', type=int)

    nb_objects, mongo_collections = mongo.get_collections("neocampus", offset, limit)

    output = {'objects': []}
    for obj in mongo_collections:
        output['objects'].append({
            'original_object_name': obj['original_object_name'],
            'swift_object_id': obj['swift_object_id'],
            'swift_user': obj['swift_user'],
            'creation_date': obj['creation_date']
        })

    output['length'] = nb_objects

    return jsonify({'result': output})
