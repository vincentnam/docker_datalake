import sys
import json

def extract_transform_load_time_series_json(json_object, swift_container, swift_id, coll, process_type):
    # TODO : process related to JSON files
    #history_data(process_type, swift_container, swift_id, "parsing_date", coll, row, result_row)
    result = json.loads(json_object)
    x = {"test": "New JSON object"}
    result.append(x)
    return result

sys.modules[__name__] = extract_transform_load_time_series_json
