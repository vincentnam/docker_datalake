from flask import Blueprint, jsonify, request, current_app
from ..services import sqldb, keystone
from datetime import datetime
import json

sqldb_data_bp = Blueprint('sqldb_data_bp', __name__)



@sqldb_data_bp.route('/measurementsSGE', methods=['GET', 'POST'])
def get_all_measurements():
    """
    ---
    post:
        requestBody:
            required: true
            content:
                application/json:
                    schema: InputSchema
        description: get all measurements
        responses:
            '200':
                description: call successful
        tags:
            - sqldb_router
    """

    try:
        token = request.get_json()['token']
    except:
        return jsonify({'error': 'Missing token'})

    if keystone.login_token(current_app.config['KEYSTONE_URL'], token) == False:
        return jsonify({'error': 'Wrong Token'})

    client = sqldb.connection_sqldb()

    # Execute the query
    results = sqldb.get_all_measurements()

    # Flatten output results into list of measurements
    measurements = [row for table in results for row in table]

    all_measurements = {
        "measurements": measurements
    }
    
    return jsonify(all_measurements)


@sqldb_data_bp.route('/topicsSGE', methods=['GET', 'POST'])
def get_all_topics():
    """
    ---
    post:
        requestBody:
            required: true
            content:
                application/json:
                    schema: InputSchema
        description: get all topics
        responses:
            '200':
                description: call successful
        tags:
            - sqldb_router
    """
    try:
        token = request.get_json()['token']
    except:
        return jsonify({'error': 'Missing token'})

    if keystone.login_token(current_app.config['KEYSTONE_URL'], token) == False:
        return jsonify({'error': 'Wrong Token'})

    client = sqldb.connection_sqldb()
    measurement = request.get_json()["measurement"]
    tag = "topic"

    # Execute the query
    results = sqldb.get_all_topics(measurement)

    # Flatten output results into list of topics
    topics = [row for table in results for row in table]
 
    all_topics = {
        "topics": topics
    }
    return jsonify(all_topics)


@sqldb_data_bp.route('/dataSGE', methods=['GET', 'POST'])
def get_data_SGE():
    """
    ---
    post:
        requestBody:
            required: true
            content:
                application/json:
                    schema: InputSchema
        description: get data SGE
        responses:
            '200':
                description: call successful
        tags:
            - sqldb_router
    """
    try:
        token = request.get_json()['token']
    except:
        return jsonify({'error': 'Missing token'})

    if keystone.login_token(current_app.config['KEYSTONE_URL'], token) == False:
        return jsonify({'error': 'Wrong Token'})

    client = sqldb.connection_sqldb()
 
    measurement = request.get_json()["measurement"]
    topic = request.get_json()["topic"]
    startDate = request.get_json()["startDate"]
    endDate = request.get_json()["endDate"]

    params = {
        'measurement': measurement,
        'topic': topic,
        'begin_date': startDate, 
        'end_date': endDate
    }
 
    # Execute the query
    results = sqldb.get_all_data(params)

    # Flatten output results into list of res_data
    res_data = [row for table in results for row in table]

    all_topics = {
        "dataSGE": res_data,
        "dataSGEGraph": res_data
    }
    return jsonify(all_topics)
