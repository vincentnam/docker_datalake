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


@keystone_router_bp.route('/auth-token', methods=['POST'])
def login_token():
    """
    ---
    get:
        description: login with token
        responses:
            '200':
                description: call successful
        tags:
            - keystone_router
    """
    try:
        token = request.get_json()['token']
        print(token)
    except:
        return jsonify({'error': 'Missing token'})

    if keystone.login_token(current_app.config['KEYSTONE_URL'], token) == False:
        return jsonify({'error': 'Wrong Token'})
    return "OK"


@keystone_router_bp.route('/users', methods=['POST'])
def get_users():
    """
    ---
    get:
        description: get list of users
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
    auth_url = current_app.config['KEYSTONE_URL']
	
    kc = client.Client(username=user, password=password, auth_url=auth_url)
    list_users = kc.users.list()

    return jsonify({'users': list_users})


@keystone_router_bp.route('/user_projects', methods=['POST'])
def get_user_projects():
    """
    ---
    get:
        description: get list of projects
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
    auth_url=current_app.config['KEYSTONE_URL']

    # Connection with login and password
    auth = v3.Password(
        auth_url=auth_url,
        username=user,
        password=password,
        project_id=current_app.config['PROJECT_ID'],
        user_domain_id=current_app.config['USER_DOMAIN_ID']
    )
    sess = keystone_session.Session(auth=auth)
    token = sess.get_token()
	
    kc = client.Client(username=user, password=password, auth_url=auth_url)
    list_projects = kc.projects.list()

    return jsonify({'projects': list_projects})


@keystone_router_bp.route('/user_roles', methods=['POST'])
def get_user_roles():
    """
    ---
    get:
        description: get list of roles
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
    auth_url=current_app.config['KEYSTONE_URL']

    # Connection with login and password
    auth = v3.Password(
        auth_url=auth_url,
        username=user,
        password=password,
        project_id=current_app.config['PROJECT_ID'],
        user_domain_id=current_app.config['USER_DOMAIN_ID']
    )
    sess = keystone_session.Session(auth=auth)
    token = sess.get_token()
	
    kc = client.Client(username=user, password=password, auth_url=auth_url)
    list_roles = kc.roles.list()

    return jsonify({'roles': list_roles})


@keystone_router_bp.route('/all_roles', methods=['POST'])
def get_all_roles():
    """
    ---
    get:
        description: get list of all roles
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
    auth_url=current_app.config['KEYSTONE_URL']

    sess = keystone_session.Session(auth=auth_url)
    ks = client.Client(session=sess)
    user_id = sess.get_user_id()
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
    return jsonify({'roles': list_roles})

