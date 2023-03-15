import flask
from keystoneauth1 import session as keystone_session
from keystoneauth1.identity import v3
import json
import requests

def login_token(url_keystone, token):
    # Open json for call auth with token
    f = open(os.path.join(current_app.root_path, 'json/token.json'))
    data = json.load(f)
    # Change id user by the token
    data["auth"]["identity"]["token"]["id"] = token
    data = json.dumps(data)
    header_token = {"Content-Type": "application/json", "Accept": "*/*"}
    # Requests auth token
    rep = requests.post(url_keystone + "/v3/auth/tokens", headers=header_token, data=data)
    # Verification if the key "error" is in the response of requests
    if "error" in rep.json():
        return False
    else:
        return True



def login_token_project(auth_url=url_keystone,token=token,container_name=container_name)
    # Open json for call auth with token
    f = open(os.path.join(current_app.root_path, 'json/token.json'))
    data = json.load(f)
    # Change id user by the token
    data["auth"]["identity"]["token"]["id"] = token
    data = json.dumps(data)
    header_token = {"Content-Type": "application/json", "Accept": "*/*"}
    # Requests auth token
    rep = requests.post(url_keystone + "/v3/auth/tokens", headers=header_token, data=data)
    # Verification if the key "error" is in the response of requests
    if "error" in rep.json():
        return False
    else:
        container_verif = False
        user_id = rep.json()['token']["user"]["id"]
        header = {"Content-Type": "application/json", "X-Auth-Token": token}
        # Requests for the list of project of the user
        rep_project = requests.get(current_app.config['KEYSTONE_URL']+"/v3/users/"+user_id+"/projects", headers=header)
        list_projects = []
        # Fill the list of projects
        for obj in rep_project.json()["projects"]:
            list_projects.append({
                'id': obj['id'],
                'name': obj['name']
            })
        # Verification if the container name is in the list of projects
        # If True : the call can continue else the call is stop
        for p in list_projects:
            if p['name'] == container_name:
                container_verif = True
        if container_verif:
            return True
        else:
            return False