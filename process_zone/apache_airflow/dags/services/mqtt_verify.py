import sys
from services import connection_swift

def mqtt_verify(swift_container, swift_id):
    verify = True
    swift_object = connection_swift(swift_container, swift_id)
    if "x-object-meta-source" not in swift_object[0]:
        verify = False
    return verify

sys.modules[__name__] = mqtt_verify