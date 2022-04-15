import os
import uuid
import base64
from flask import Blueprint, jsonify, current_app, request, send_from_directory, make_response
import os
from ..services import keystone
from keystoneauth1 import session as keystone_session
from keystoneauth1.identity import v3
from keystoneclient.v3 import client

swift_file_bp = Blueprint('keystone_router_bp', __name__)

@keystone_router_bp.route("/hello", methods=['GET'])
def hello():
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

    auth = v3.Password(
        auth_url=current_app.config['KEYSTONE_URL'],
        username=user,
        password=password,
        project_id='some-project',
        user_domain_name='default',
        project_domain_name='default',
    )

    session = keystone_session.Session(
        auth=auth,
        user_agent='some-app',
    )

    client = client.Client(
        session=session(),
        interface='public',
        timeout=5,
    )

    service = client.services.list(type='some-keystone-service-type')[0]
    endpoint = client.endpoints.list(service=service.id, interface='public', enabled=True)[0]
    url = endpoint.url

    print(session.get(f'{url}/test').json())
    print(client.token.id)
    return client.token.id



