#import labraries
import os
import mimetypes
import pandas as pd
from pathlib import Path
from  natsort import natsorted
from pymongo import MongoClient
import swift_connection as swift


def connction_mongodb(mongodb_url,username,password,authSource):
    try:
        conn = MongoClient(mongodb_url, username=username, password=password, authSource=authSource, connect=False)
        print("[INFO] Connecting to MongoDB server")
        return conn
    except:
        print("Could not connect to MongoDB Server")
def get_id(connection_mongo):
    return connection_mongo.stats.swift.find_one_and_update({"type": "object_id_file"}, {"$inc": {"object_id": 1}})["object_id"]
def insert_indexes_images(connection_mongo,connection_swift,path_csv_indexes,path_director_images):
    db = connection_mongo.images
    dataset_index = db.data_index
    # CSV file indexes
    data_csv_indexes = open(path_csv_indexes, 'r')
    df = pd.read_csv(data_csv_indexes, delimiter=',', quotechar='"', header=None)
    id_swift = get_id(connection_mongo)
    #name_image_swift = natsorted(os.listdir(path_director_images))
    #name_image_swift = sorted(os.listdir(path_director_images))
    for i in range(len(df)):
        name_image_mongo = df[0][i].split('\\')[-1]
        name_image_swift = os.listdir(path_director_images)[i]
        path_image = os.path.join(path_director_images, os.listdir(path_director_images)[i])
        type_file = str(mimetypes.guess_type(path_image)[0])
        container_name = "data_descriptor"
        if name_image_mongo == name_image_swift :
            id_swift +=1
            vectors = df.iloc[:, 1:]
            file_content = Path(path_image).read_bytes()
            index = {
                "name_image": name_image_mongo,
                "contenet_type": type_file,
                "id_swift": str(id_swift),
                "vector": vectors.loc[i].tolist()
            }
            swift.set_swift(connection_swift, container_name,str(id_swift),file_content,type_file)
            #connection_swift.put_object(container_name,str(id_swift),contents=file_content,content_type=type_file)
            dataset_index.insert_one(index)
    print("[INFO] End of Inserting")
