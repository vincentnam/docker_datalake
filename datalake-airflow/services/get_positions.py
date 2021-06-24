import sys

def get_positions(columns, timestamp_fields_list, value_fields_list):
    # Search position of filds timestamp, value, topic and value_units
    position_timestamp = ""
    position_value = ""
    position_topic = ""
    position_payload_value_units = ""
    for key, value in enumerate(columns):
        if value in timestamp_fields_list :
            position_timestamp = value
        if value in value_fields_list :
            position_value = value
        if value == "topic":
            position_topic = value
        if value == "payload.value_units":
            position_payload_value_units = value

    return position_timestamp, position_value, position_topic, position_payload_value_units


sys.modules[__name__] = get_positions
