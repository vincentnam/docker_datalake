import swiftclient

#
class SwiftTools:

    def __init__(self, user, key, authurl):
        self.conn = swiftclient.Connection(user=user, key=key,
                                      authurl=authurl)

    def get_object(self, swift_id, container_name):
        return self.conn.get_object(container_name, swift_id)