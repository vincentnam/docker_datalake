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
    # Connection with login and password
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

    # Connection with admin for return roles of user
    admin_auth = v3.Password(
        auth_url=current_app.config['KEYSTONE_URL'],
        username=current_app.config['USER_ADMIN'],
        password=current_app.config['USER_ADMIN_PWD'],
        project_id=current_app.config['PROJECT_ID'],
        user_domain_id=current_app.config['USER_DOMAIN_ID']
    )
    admin_sess = keystone_session.Session(auth=admin_auth)
    admin_ks = client.Client(session=admin_sess)
    list_roles = []
    for project in list_projects:
        roles = admin_ks.roles.list(user=user_id, project=project['id'])
        for obj in roles:
            list_roles.append({
                'id': obj.id,
                'name': obj.name,
                'project': project["name"]
            })

    return jsonify({'token': token, 'projects': list_projects, 'roles': list_roles})
