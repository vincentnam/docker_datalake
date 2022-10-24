import swiftclient

def connection_swift(authurl,user,key):
    # Connection à Swift
    try:
        conn = swiftclient.Connection(
            user=user,
            key=key,
            authurl=authurl,
            insecure=True
        )
        print("[INFO] Connecting to Swift Server")
        return conn
    except:
        print("Could not connect to Swift Server")

def set_swift(conn,swift_container,swift_id,file_content,type_file):
    #insertion de l'objet swift
    conn.put_object(swift_container,swift_id,contents=file_content,content_type =type_file)
    print("[INFO] Inserting a row into container")

def get_swift(conn, swift_container, swift_id):
    # Récupération de l'object Swift
    swift_object = conn.get_object(swift_container, swift_id)
    print("[INFO] Geting a row from container")
    return swift_object

