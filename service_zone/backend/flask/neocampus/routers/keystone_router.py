import os
import uuid
import base64
from flask import Blueprint, jsonify, current_app, request
import os
from ..services import keystone
from keystoneauth1 import session as keystone_session
from keystoneauth1.identity import v3
from keystoneclient.v3 import client


keystone_router_bp = Blueprint('keystone_router_bp', __name__)

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

    try:
        params = {
            'user': request.get_json()['user'],
            'password': request.get_json()['password']
        }
    except:
        return jsonify({'error': 'Missing required fields.'})

    user = params['user']
    password = params['password']
    auth = v3.Password(
        auth_url=current_app.config['KEYSTONE_URL'],
        username=user,
        password=password,
        project_id=current_app.config['PROJECT_ID'],
        user_domain_id=current_app.config['USER_DOMAIN_ID']
    )
    sess = keystone_session.Session(auth=auth)
    token = sess.get_token()
    user_id = sess.get_user_id()
    ks = client.Client(session=sess)
    projects = ks.projects.list(user=user_id)
    list_projects = []
    for obj in projects:
        list_projects.append({
            'id': obj.id,
            'name': obj.name
        })
    return jsonify({'token': token, 'projects': list_projects})
