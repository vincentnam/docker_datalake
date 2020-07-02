import swiftclient

#
# class SwiftTools:

def get_object(swift_id, container_name, user, key, authurl):
    conn = swiftclient.Connection(user=user, key=key,
                                  authurl=authurl)
    return conn.get_object(container_name, swift_id)