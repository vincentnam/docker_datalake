# import the necessary packages
import os
import json
import io
import uuid
from PIL import Image
import numpy as np
from ..similarity import swift_connection
from flask import Blueprint, jsonify, request, current_app

class Searcher:
    def __init__(self, data_index, connection_swift):
        # store our index path
        self.data_index = data_index
        self.connection_swift = connection_swift

    def chi2_distance(self, A, B, eps = 1e-10):
        # compute the chi-squared distance
        d = 0.5 * np.sum([((int(a) - int(b)) ** 2) / (int(a) + int(b) + eps) for (a, b) in zip(A, B)])
        return d

    def search(self, queryFeatures, limit=10):
        container_name = "data_descriptor"
        #Active or not the delete of similarity in the directory IMAGES_SIMILARITY
        #files_path = f"{current_app.config['IMAGES_SIMILARITY']}"
        #dir = os.path.join(current_app.root_path, files_path)
        #for f in os.listdir(dir):
        #    os.remove(os.path.join(dir, f))

        # initialize our dictionary of results
        results = {}
        images_list = []
        cursor = self.data_index.find()
        # loop over the rows in the data_index
        for rep in cursor:
            features = rep['vector']
            d = self.chi2_distance(features, queryFeatures)
            results[rep['id_swift']] = int(d)
        # sort our results, so that the smaller distances (i.e. the
        # more relevant images are at the front of the list)
        results = sorted([(v, k) for (k, v) in results.items()])
        results = [(v, k) for (k, v) in results]
        results = results[:][:limit]
        keys = [keys for keys, value in results]
        data_image = [swift_connection.get_swift(self.connection_swift,container_name,key) for key in keys]
        images = []
        for data in data_image:
            image = data[1]
            file_path = f"{current_app.config['IMAGES_SIMILARITY']}similarity_{str(uuid.uuid4().hex)}.png"
            f = open(os.path.join(current_app.root_path, file_path), 'ab')
            f.write(image)
            f.close()
            ipath = os.path.join(current_app.config['HOST_URL'], 'api', file_path)
            images.append(ipath)

        json_data = json.dumps(images)
        return json_data
