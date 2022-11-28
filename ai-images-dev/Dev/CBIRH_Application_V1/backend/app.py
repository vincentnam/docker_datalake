# Import the flask web server
import os
import cv2
import urllib3
import numpy as np
import searcher as sr
from PIL import Image
import descriptor as dc
from dotenv import load_dotenv
from flask import Flask,request
from swift_connection import connection_swift
from mongodb_connection import connction_mongodb

#Disable  InsecureRequestWarning
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
# Single module that grabs all modules executing from this file
app = Flask(__name__)
#Env variables
load_dotenv()
MONGO_URL = os.getenv('MONGO_URL')
MONGO_ADMIN = os.getenv('MONGO_ADMIN')
MONGO_PWD = os.getenv('MONGO_PWD')
MONGO_DB_AUTH = os.getenv('MONGO_DB_AUTH')
SWIFT_AUTHURL = os.getenv('SWIFT_AUTHURL')
SWIFT_USER = os.getenv('SWIFT_USER')
SWIFT_KEY = os.getenv('SWIFT_KEY')
UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER')

#Home route
@app.route('/')
def home():
    return {"message": "Welcome to the Data Lake Eye"}

# Similarity route
@app.route('/similarity', methods=['GET', 'POST'])
def upload_file():
   # Upload image request
   f = request.files['file']
   path = os.path.join(UPLOAD_FOLDER, f.filename)
   f.save(path)

   # Connection databases (mongo/swift)
   connection_mongo = connction_mongodb(MONGO_URL, MONGO_ADMIN, MONGO_PWD, MONGO_DB_AUTH)
   connection_swiftclients = connection_swift(SWIFT_AUTHURL, SWIFT_USER, SWIFT_KEY)


   # Dataset of indexes
   dataset_index = connection_mongo.images.data_index

   #Open image request
   image = Image.open(path)

   search = sr.Searcher(dataset_index, connection_swiftclients)
   descriptor = dc.Descriptor()
   features = descriptor.image_query_describe(cv2.cvtColor(np.asarray(image), cv2.COLOR_BGR2RGB))
   Images = search.search(features)
   return Images

if __name__ == "__main__":
    app.run(debug=True)