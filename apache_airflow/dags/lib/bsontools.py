from bson import decode_file_iter, encode

# class BsonTools:

def bson_to_json(file):
    '''
    :param file: str : path to the file
    :return: iterator : for each document in the bson file

    '''
    try:
        with open(file, "rb") as fp :
            return decode_file_iter(fp)
    except FileNotFoundError as nosuchfile:
        raise nosuchfile


def json_to_bson(json):
    try :
        return encode(json)
    except Exception as e:
        raise e
