import sys
import swiftclient.service
from swiftclient.service import SwiftService
import swiftclient
import config

# Function return swift_object of a swift_id 
def connection_swift(swift_container, swift_id):
    # Openstack Swift
    authurl = config.url_swift
    user = config.user_swift
    key = config.key_swift
    # Connction à Swift
    conn = swiftclient.Connection(
        user=user,
        key=key,
        authurl=authurl,
        insecure=True
    )
    # Récupération de l'object Swift
    swift_object = conn.get_object(swift_container, swift_id)
    print('----------- OBJET SWIFT -------------')
    # print(swift_object)

    return swift_object
    

sys.modules[__name__] = connection_swift
