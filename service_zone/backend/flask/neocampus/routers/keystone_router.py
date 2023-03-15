import os
import uuid
import base64
from flask import Blueprint, jsonify, current_app, request, g
import os
from ..services import keystone
from keystoneauth1 import session as keystone_session
from keystoneauth1.identity import v3
from keystoneclient.v3 import client

import requests

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
    data_admin_token = '{ "auth": {"identity": {"methods": ["password"],"password": ' \
           '{"user": {"name": "' + current_app.config['USER_ADMIN'] + '","project":{"name":"' + current_app.config['PROJECT_ID'] + '"},' \
                                                                                                                 ' "domain": { "name": "' + \
           current_app.config['USER_DOMAIN_ID'] + '" },' \
                                                  '"password": "' + current_app.config['USER_ADMIN_PWD'] + \
           '"}}},"scope": {"domain": {"name": "' + current_app.config['USER_DOMAIN_ID'] + '"}}}}'
    header_admin_token = {"Content-Type": "application/json", "Accept": "*/*"}

    admin_rep = requests.post(current_app.config['KEYSTONE_URL'] + "/auth/tokens", headers=header_admin_token, data=data_admin_token)
    # admin_rep = requests.post(current_app.config['KEYSTONE_URL'] + "auth/tokens", headers=,
    #                     data=, verify=False)
    # admin_token = admin_rep.headers["X-Subject-Token"]
    # Connection with login and password

    header = {"Content-Type": "application/json", "Accept": "*/*"}
    data = '{ "auth": {"identity": {"methods": ["password"],"password": ' \
       '{"user": {"name": "' + user + '","project":{"name":"' + current_app.config['PROJECT_ID'] + '"},' \
                                           ' "domain": { "name": "' + current_app.config['USER_DOMAIN_ID'] + '" },' \
 '"password": "' + password + '"}}},"scope": {"domain": {"name": "' + current_app.config['USER_DOMAIN_ID'] + '"}}}}'
    rep = requests.post(current_app.config['KEYSTONE_URL'] + "/auth/tokens", headers=header, data=data)
    token = rep.headers["X-Subject-Token"]
    list_roles = rep.json()['token']["roles"]
    user_id = rep.json()['token']["user"]["id"]
    header = {"Content-Type": "application/json", "X-Auth-Token": token}
    rep_project = requests.get(current_app.config['KEYSTONE_URL']+"/users/"+user_id+"/projects", headers=header)
    list_projects = rep_project.json()["projects"]
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
    except:
        return jsonify({'error': 'Missing token'})

    if keystone.login_token(current_app.config['KEYSTONE_URL'], token) == False:
        return jsonify({'error': 'Wrong Token'})
    data ='{ "auth": {     "identity": {       "methods": ["token"], "token": {"id": "'+token+'"}}}}'

    header = {"Content-Type": "application/json", "Accept": "*/*"}
    rep = requests.post(current_app.config['KEYSTONE_URL'] + "/auth/tokens", headers=header, data=data)
    print(rep.json())
    print(rep.headers)
    user_id = rep.json()['token']["user"]["id"]
    list_roles = rep.json()['token']["roles"]
    header = {"Content-Type": "application/json", "X-Auth-Token": token}
    rep_project = requests.get(current_app.config['KEYSTONE_URL'] + "/users/" + user_id + "/projects", headers=header)
    print("COUCOU")
    print(rep_project.json())
    print(rep_project.headers)
    list_projects = rep_project.json()["projects"]

    # auth = v3.token.Token(auth_url=current_app.config['KEYSTONE_URL'], token=token)
    # sess = keystone_session.Session(auth=auth)
    # ks = client.Client(session=sess)
    # user_id = sess.get_user_id()
    # projects = ks.projects.list(user=user_id)
    # list_projects = []
    # for obj in projects:
    #     list_projects.append({
    #         'id': obj.id,
    #         'name': obj.name
    #     })
    # # Connection with admin for return roles of user
    # admin_auth = v3.Password(
    #     auth_url=current_app.config['KEYSTONE_URL'],
    #     username=current_app.config['USER_ADMIN'],
    #     password=current_app.config['USER_ADMIN_PWD'],
    #     project_id=current_app.config['PROJECT_ID'],
    #     user_domain_id=current_app.config['USER_DOMAIN_ID']
    # )
    # admin_sess = keystone_session.Session(auth=admin_auth)
    # admin_ks = client.Client(session=admin_sess)
    # list_roles = []
    # for project in list_projects:
    #     roles = admin_ks.roles.list(user=user_id, project=project['id'])
    #     for obj in roles:
    #         list_roles.append({
    #             'id': obj.id,
    #             'name': obj.name,
    #             'project': project["name"]
    #         })
    return jsonify({'projects': list_projects, 'roles': list_roles})

@keystone_router_bp.route('/auth-token/projects', methods=['POST'])
def login_token_projects():
    """
    ---
    get:
        description: login with token and return list projects
        responses:
            '200':
                description: call successful
        tags:
            - keystone_router
    """
    try:
        token = request.get_json()['token']
    except:
        return jsonify({'error': 'Missing token'})

    if keystone.login_token(current_app.config['KEYSTONE_URL'], token) == False:
        return jsonify({'error': 'Wrong Token'})

    auth = v3.token.Token(auth_url=current_app.config['KEYSTONE_URL'], token=token)
    sess = keystone_session.Session(auth=auth)
    ks = client.Client(session=sess)
    user_id = sess.get_user_id()
    projects = ks.projects.list(user=user_id)
    list_projects = []
    for obj in projects:
        list_projects.append({
            'id': obj.id,
            'name': obj.name
        })
    return jsonify({'projects': list_projects})

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
        token = request.get_json()['token']
    except:
        return jsonify({'error': 'Missing required fields.'})

    if keystone.login_token(current_app.config['KEYSTONE_URL'], token) == False:
        return jsonify({'error': 'Wrong Token'})

    admin_auth = v3.token.Token(
        auth_url=current_app.config['KEYSTONE_URL'],
        token=token,
        project_id=current_app.config['PROJECT_ID']
    )
    admin_sess = keystone_session.Session(auth=admin_auth)
    admin_ks = client.Client(session=admin_sess)
    users = admin_ks.users.list()

    list_users = []
    for obj in users:
        list_users.append({
            'id': obj.id,
            'name': obj.name,
        })
    return jsonify({'users': list_users})


@keystone_router_bp.route('/user_assignment', methods=['POST'])
def get_user_projects():
    """
    ---
    get:
        description: get list of assignment of a user
        responses:
            '200':
                description: call successful
        tags:
            - keystone_router
    """
    try:
        token = request.get_json()['token']
        user_id = request.get_json()['user_id']
    except:
        return jsonify({'error': 'Missing required fields.'})

    if keystone.login_token(current_app.config['KEYSTONE_URL'], token) == False:
        return jsonify({'error': 'Wrong Token'})

    admin_auth = v3.token.Token(
        auth_url=current_app.config['KEYSTONE_URL'],
        token=token,
        project_id=current_app.config['PROJECT_ID']
    )
    admin_sess = keystone_session.Session(auth=admin_auth)
    admin_ks = client.Client(session=admin_sess)

    assignments = admin_ks.role_assignments.list(user=user_id)
    list_assignments = []
    for obj in assignments:
        if 'project' in obj.scope.keys():
            list_assignments.append({
                'role': {
                    'id': obj.role['id'],
                    'name': admin_ks.roles.get(obj.role['id']).name,
                },
                'project': {
                    'id': obj.scope['project']['id'],
                    'name': admin_ks.projects.get(obj.scope['project']['id']).name,
                },
            })
    return jsonify({'assignment': list_assignments})


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
        token = request.get_json()['token']
    except:
        return jsonify({'error': 'Missing required fields.'})

    if keystone.login_token(current_app.config['KEYSTONE_URL'], token) == False:
        return jsonify({'error': 'Wrong Token'})

    admin_auth = v3.token.Token(
        auth_url=current_app.config['KEYSTONE_URL'],
        token=token,
        project_id=current_app.config['PROJECT_ID']
    )
    admin_sess = keystone_session.Session(auth=admin_auth)
    admin_ks = client.Client(session=admin_sess)
    roles = admin_ks.roles.list()
    list_roles = []
    for obj in roles:
        list_roles.append({
            'id': obj.id,
            'name': obj.name,
        })

    return jsonify({'roles': list_roles})


@keystone_router_bp.route('/all_projects', methods=['POST'])
def get_all_projects():
    """
    ---
    get:
        description: get list of all projects
        responses:
            '200':
                description: call successful
        tags:
            - keystone_router
    """
    try:
        token = request.get_json()['token']
    except:
        return jsonify({'error': 'Missing required fields.'})

    if keystone.login_token(current_app.config['KEYSTONE_URL'], token) == False:
        return jsonify({'error': 'Wrong Token'})

    admin_auth = v3.token.Token(
        auth_url=current_app.config['KEYSTONE_URL'],
        token=token,
        project_id=current_app.config['PROJECT_ID']
    )
    admin_sess = keystone_session.Session(auth=admin_auth)
    admin_ks = client.Client(session=admin_sess)
    projects = admin_ks.projects.list()
    list_projects = []
    for obj in projects:
        list_projects.append({
            'id': obj.id,
            'name': obj.name,
        })
    return jsonify({'projects': list_projects})


@keystone_router_bp.route('/role_assignments/add', methods=['POST'])
def role_assignments_create():
    """
    ---
    get:
        description: create a assigment with a user, a project and a role
        responses:
            '200':
                description: call successful
        tags:
            - keystone_router
    """
    try:
        token = request.get_json()['token']
        user = request.get_json()['user']
        role = request.get_json()['role']
        project = request.get_json()['project']
    except:
        return jsonify({'error': 'Missing token'})

    if keystone.login_token(current_app.config['KEYSTONE_URL'], token) == False:
            return jsonify({'error': 'Wrong Token'})

    admin_auth = v3.token.Token(
        auth_url=current_app.config['KEYSTONE_URL'],
        token=token,
        project_id=current_app.config['PROJECT_ID']
    )
    admin_sess = keystone_session.Session(auth=admin_auth)
    admin_ks = client.Client(session=admin_sess)
    admin_ks.roles.grant(role=role,user=user,project=project)
    return jsonify({'role_assignments': "Add"})

@keystone_router_bp.route('/role_assignments/delete', methods=['POST'])
def role_assignments_delete():
    """
    ---
    get:
        description: create a assigment with a user, a project and a role
        responses:
            '200':
                description: call successful
        tags:
            - keystone_router
    """
    try:
        token = request.get_json()['token']
        user = request.get_json()['user']
        role = request.get_json()['role']
        project = request.get_json()['project']
    except:
        return jsonify({'error': 'Missing token'})

    if keystone.login_token(current_app.config['KEYSTONE_URL'], token) == False:
            return jsonify({'error': 'Wrong Token'})

    admin_auth = v3.token.Token(
        auth_url=current_app.config['KEYSTONE_URL'],
        token=token,
        project_id=current_app.config['PROJECT_ID']
    )
    admin_sess = keystone_session.Session(auth=admin_auth)
    admin_ks = client.Client(session=admin_sess)
    admin_ks.roles.revoke(role=role,user=user,project=project)
    return jsonify({'role_assignments': "Delete"})


@keystone_router_bp.route('/role_assignments/purge', methods=['POST'])
def role_assignments_purge():
    """
    ---
    get:
        description: purge users
        responses:
            '200':
                description: call successful
        tags:
            - keystone_router
    """
    try:
        token = request.get_json()['token']
    except:
        return jsonify({'error': 'Missing token'})

    if keystone.login_token(current_app.config['KEYSTONE_URL'], token) == False:
            return jsonify({'error': 'Wrong Token'})

    admin_auth = v3.token.Token(
        auth_url=current_app.config['KEYSTONE_URL'],
        token=token,
        project_id=current_app.config['PROJECT_ID']
    )
    admin_sess = keystone_session.Session(auth=admin_auth)
    admin_ks = client.Client(session=admin_sess)
    users = admin_ks.users.list()
    user_list = []
    for user in users:
        user_list.append(user.id)
    assignments = admin_ks.role_assignments.list()
    
    for obj in assignments:
         if 'project' in obj.scope.keys() and obj.user['id'] not in user_list:
            admin_ks.roles.revoke(obj.role['id'], user=obj.user['id'], project=obj.scope['project']['id'])

    return jsonify({'status': 'ok'})
    