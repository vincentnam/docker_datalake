# Variables

## ./backend/
### ./flask/
#### ./neocampus/


|./backend/flask/neocampus/__init__.py||
|--|--|
|MONGO_URL | mongo db URL (used for MongoClient() from pymongo python lib)|
|SWIFT_AUTHURL | authentication URL for Swift |
|SWIFT_USER | swift user for authentication |
|SWIFT_KEY | swift pass corresponding to SWIFT_USER|
|SWIFT_FILES_DIRECTORY| "xxx"|

#### ./neocampus/routers/
|./backend/flask/routers/swift_file.py||
|--|--|
| container_name (def storage() ) | container to which upload the file| 

See variables for metadata and swift parameters.

#### ./uwsgi/

|./backend/flask/uwsgi/uwsgi.ini||
|--|--|
|**socket** | url + TCP port |
| module | module to deploy (see ./neocampus/__init__.py)|

### ./nginx/ : 
> TODO : comment default.conf and uwsgi_params

|./backend/nginx/uwsgi_params||
|--|--|
|**server_name** | server URL|
|**listen** |port to listen to|
|**Access-Control-Allow-Origin** || 
    
## ./fronted/ :
### /datalake-react-front/ : 

|./frontend/datalake-react-front/src/api/api.js||
|--|--|
|baseURL| URL for ? in axios.create()|


|./frontend/datalake-react-front/docker-compose.yml||
|--|--|
|volumes| for app and node_modules -> may be heavy folders|
|ports| 3001 -> host port / 3000 -> in container port (default react port) |

|./frontend/datalake-react-front/src/components/download-page/Download.js||
|--|--|
|url| URL for ?|
|perPage| ?|


    