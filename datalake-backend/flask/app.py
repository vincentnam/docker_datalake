import os
from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
import pymongo

app = Flask(__name__)
CORS(app)

@app.route('/')
def hello():
    return 'Hello Modis!'

@app.route('/storage')
def storage():
    idType = request.args.get('idType')
    print(idType)
    data =  request.args.get('data')
    print(data)
    premieremeta =  request.args.get('premieremeta')
    print(premieremeta)
    deuxiememeta =  request.args.get('deuxiememeta')
    print(deuxiememeta)
    
    retour = dict()
    retour = {"retour": {
        "idType": idType,
        "data": data,
        "premieremeta": premieremeta,
        "deuxiememeta": deuxiememeta
    }}
    print(retour)
    
    return jsonify(retour)


@app.route('/raw-data')
def get_metadata():


    limit = request.args.get('limit', type = int)
    offset = request.args.get('offset', type = int)

    mongoClient = pymongo.MongoClient(os.environ.get('url'))
    db = mongoClient["swift"]
    collection = db["neocampus"]
    nb_objects = collection.find().count()

    output = {'objects': []}
    for obj in collection.find().skip(offset).limit(limit):
        output['objects'].append({ 
            'original_object_name' : obj['original_object_name'], 
            'swift_object_id': obj['swift_object_id'],
            'swift_user': obj['swift_user'],
            'creation_date': obj['creation_date']
        })
    
    output['length'] = nb_objects
    print(output)

    return jsonify({'result' : output})

'''@app.route("/raw-file")
def getPlotCSV():
    return send_file('sensors.csv',
        mimetype='text/csv',
        attachment_filename='sensors.csv',
        as_attachment=True
    )
'''

if __name__ == '__main__':
    app.run()
