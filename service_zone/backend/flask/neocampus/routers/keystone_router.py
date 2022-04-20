import os
import uuid
import base64
from flask import Blueprint, jsonify, current_app, request
import os
from ..services import keystone
from keystoneauth1 import session as keystone_session
from keystoneauth1.identity import v3
from keystoneauth1 import token_endpoint

keystone_router_bp = Blueprint('keystone_router_bp', __name__)

@keystone_router_bp.route("/hello", methods=['GET'])
def hello():
    """
    ---
    get:
        description: Test
        responses:
            '200':
                description: call successful
        tags:
            - keystone_router
    """
    ctx = keystone.get_oslo_context()
    return f'Hello, {ctx.user_id} on project {ctx.project_id}!'


@keystone_router_bp.route('/login', methods=['POST'])
def login():
    """
    ---
    get:
        description: login to keystone and react
        responses:
            '200':
                description: call successful
        tags:
            - keystone_router
    """
    user = request.get_json()['user']
    password = request.get_json()['password']
    print(user)
    print(password)
    print(current_app.config['KEYSTONE_URL'])

    auth = v3.Password(
        auth_url=current_app.config['KEYSTONE_URL'],
        username=user,
        password=password,
        project_id=current_app.config['PROJECT_ID'],
        user_domain_id=current_app.config['USER_DOMAIN_ID']
    )
    #auth = token_endpoint.Token(current_app.config['KEYSTONE_URL'],token="token")


    sess = keystone_session.Session(auth=auth)
    #print(sess.get("/v3/users", endpoint_filter={'service_type': 'identity'}))
    return sess.get_token()



