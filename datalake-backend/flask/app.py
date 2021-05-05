from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/')
def hello():
    return 'Hello Modis!'

@app.route('/raw-data')
def get_metadata():
    import pymongo

    limit = request.args.get('limit', type = int)
    offset = request.args.get('offset', type = int)

    mongoClient = pymongo.MongoClient("mongodb://localhost:27017/")
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


if __name__ == '__main__':
    app.run()
