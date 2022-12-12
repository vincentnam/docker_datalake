import os
import cv2
import urllib3
import numpy as np
from PIL import Image
from dotenv import load_dotenv
from ..similarity import descriptor as dc
from ..similarity import searcher as sr
from ..similarity import mongodb_connection, swift_connection
from flask import Blueprint, jsonify, request, current_app
from ..services import swift, mongo, keystone


similarity_bp = Blueprint('similarity_bp', __name__)

@similarity_bp.route('/similarity', methods=['GET', 'POST'])
def upload_file():

    token = request.form["token"]

    if keystone.login_token(current_app.config['KEYSTONE_URL'], token) == False:
        return jsonify({'error': 'Wrong Token'})

    # Upload image request
    f = request.files['file']
    path = os.path.join(current_app.root_path,current_app.config['UPLOAD_FOLDER'], f.filename)
    f.save(path)

    # Connection databases (mongo/swift)
    connection_mongo = mongodb_connection.connection_mongodb(current_app.config['MONGO_URL'], current_app.config['MONGO_ADMIN'], current_app.config['MONGO_PWD'],current_app.config['MONGO_DB_AUTH'])
    connection_swiftclients = swift_connection.connection_swift(current_app.config['SWIFT_AUTHURL'], current_app.config['SWIFT_USER'], current_app.config['SWIFT_KEY'])

    # Dataset of indexes
    dataset_index = connection_mongo.images.data_index

    #Open image request
    image = Image.open(path)

    search = sr.Searcher(dataset_index, connection_swiftclients)
    descriptor = dc.Descriptor()
    features = descriptor.image_query_describe(cv2.cvtColor(np.asarray(image), cv2.COLOR_BGR2RGB))
    Images = search.search(features)
    return Images
