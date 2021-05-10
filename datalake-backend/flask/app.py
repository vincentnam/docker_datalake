import os
from flask import Flask, jsonify, request, send_file
from flask_cors import CORS


app = Flask(__name__)
CORS(app)

@app.route('/')
def hello():
    return 'Hello Modis!'

<<<<<<< HEAD
@app.route('/storage', methods= ['GET', 'POST'])
def storage(self):
    idType = request.form['idType']
    print(idType)
    data =  request.form['data']
    print(data)
    premieremeta =  request.form['premieremeta']
    print(premieremeta)
    deuxiememeta =  request.form['deuxiememeta']
    print(deuxiememeta)
    
    return 'storage'


@app.route('/raw-data')
def get_metadata():
    import pymongo

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
