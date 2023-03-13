import flask
from keystoneauth1 import session as keystone_session
from keystoneauth1.identity import v3
import json

def login_token(url_keystone, token):
#     f = open('json/token.json')
#     data = json.load(f)
#     data["auth"]["identity"]["token"]["id"] = token
#     header_token = {"Content-Type": "application/json", "Accept": "*/*"}
#
#     reponse = requests.post(current_app.config['KEYSTONE_URL'] + "/v3/auth/tokens", headers=header_token, data=data)

    auth = v3.token.Token(auth_url=url_keystone,token=token)
    sess = keystone_session.Session(auth=auth)
    if sess.get_user_id() == None:
        return False
    else:
        return True
