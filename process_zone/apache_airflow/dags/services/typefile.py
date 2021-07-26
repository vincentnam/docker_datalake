import sys

def typefile(typef):
    type_file = ""
    #Research the type file in function of the extension file
    if(typef == "txt"):
        type_file = "text/plain"
    if(typef == "xls" or typef == "xlsx" or typef == "csv"):
        type_file = "application/vnd.ms-excel"
    if(typef == "png"):
        type_file = "image/png"
    if(typef == "jpg" or typef == "jpeg"):
        type_file = "image/jpeg"
    if(typef == "json"):
        type_file = "application/json"
    if(typef == "json"):
        type_file = "application/json"
    if(typef == "json"):
        type_file = "application/json"
    if(typef == "zip"):
        type_file = "application/x-zip-compressed"
    if(typef == "tar"):
        type_file = "application/x-gzip"
    
    return type_file

sys.modules[__name__] = typefile