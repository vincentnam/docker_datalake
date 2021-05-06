import os
from flask import Flask, jsonify, request, send_file, url_for
import io, pathlib
from zipfile import ZipFile
from flask_cors import CORS

app = Flask(
    __name__,
    static_folder='static'    
)

CORS(app)

@app.route('/')
def hello():
    return 'Hello Modis!'

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

    return jsonify({'result' : output})
  
'''def get_all_file_paths(directory):
  
    # initializing empty file paths list
    file_paths = []
  
    # crawling through directory and subdirectories
    for root, directories, files in os.walk(directory):
        for filename in files:
            # join the two strings in order to form the full filepath.
            filepath = os.path.join(root, filename)
            file_paths.append(filepath)

    # returning all file paths
    return file_paths        
  

@app.route("/raw-file")
def getPlotCSV():
   # path to folder which needs to be zipped
    directory = './files'
  
    # calling function to get all file paths in the directory
    file_paths = get_all_file_paths(directory)
    folder = 'static'
    zipped_filename = "my_python_files.zip"
  
    # writing files to a zipfile
    with ZipFile(folder+'/'+zipped_filename,'w') as zip:
        # writing each file one by one
        for file in file_paths:
            zip.write(file)
        
    #data.seek(0)
    #send_file(
    #    data,
    #    mimetype='application/zip',
    #    as_attachment=False,
    #    attachment_filename='data.zip'
    #)

    full_url = request.url_root + url_for('static', filename='my_python_files.zip')
    return full_url
    '''

if __name__ == '__main__':
    app.run()
