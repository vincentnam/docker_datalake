import os

import swiftclient
from flask import current_app
from .mongo import get_swift_original_object_name


def download_object_file(container_name, object_id):
    """
    convert swift object to file and down it
    :param container_name: swift container name
    :param object_id: swift object id
    :return: saved file path in flask
    """
    swift_conn = swiftclient.Connection(user=current_app.config['SWIFT_USER'], key=current_app.config['SWIFT_KEY'],
                                        authurl=current_app.config['SWIFT_AUTHURL'])
    swift_object_raw = swift_conn.get_object(container_name, object_id)

    original_object_name = get_swift_original_object_name(container_name, object_id)

    # save file
    file_path = f"{current_app.config['SWIFT_FILES_DIRECTORY']}/{original_object_name}"
    f = open(os.path.join(current_app.root_path, file_path), 'wb')
    f.write(swift_object_raw[1])
    f.close()

    return file_path


def upload_object_file(container_name, object_id, data, filesType):
    """
    convert swift object to file and down it
    :param container_name: swift container name
    :param object_id: swift object id
    :return: saved file path in flask
    """
    swift_conn = swiftclient.Connection(user=current_app.config['SWIFT_USER'], key=current_app.config['SWIFT_KEY'],
                                        authurl=current_app.config['SWIFT_AUTHURL'])
    original_object_name = swift_conn.get_swift_original_object_name(container_name, object_id)

    # save file
    
    file_path = f"{current_app.config['SWIFT_FILES_DIRECTORY']}/{original_object_name}.txt"
    f = open(os.path.join(current_app.root_path, file_path), 'wb')
    
    f.write(data)
    f.close()

    return file_path
