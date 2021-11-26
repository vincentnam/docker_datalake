import sys
import config
from io import StringIO

# Handling function about SQL dumps
def extract_transform_load_sge(swift_result, swift_container, swift_id, process_type):

    # Start of treatment 
    s=str(swift_result,'utf-8').replace("\\n", "\n")
    lines = StringIO()
    lines.write(s)
    lines.seek(0)
    data = []
    for line in lines:
        line = line.replace("\n","")
        data.append(line)
    
    return [{'result': 'Insert done'}]

sys.modules[__name__] = extract_transform_load_sge