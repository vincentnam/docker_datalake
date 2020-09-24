# TODO : create tools to process JSON :
#    - TODO : create tools to process sensor log into InfluxDB
#    - TODO : IA FOR JSON TEMPLATE : AUTOMATIC TEMPLATE / INFORMATION RECOGNITION FOR A LIST OF DOCUMENT WITH DIFFERENTS STRUCTURE

# { "_id" : ObjectId("5d004092adf80168fe79b55c"),
# "idcapteur" : 4, "subId" : "ouest", "device" : "temperature",
# "data" : { "date" : "2019-06-12T00:00:18.388374",
#            "payload" : { "subID" : "ouest", "input" : 117,
#            "value_units" : "celsius", "value" : "15.00", "unitID" : "outside" },
#            "uri" : "u4/302/temperature/ouest" },
#            "mesurevaleur" : [ { "idlibv" : 1, "valeur" : 15 } ],
#            "building" : "u4", "room" : "302", "idpiece" : 1, "uri" : "u4/302/temperature/ouest", "idMesure" : 46739984, "datemesure" : ISODate("2019-06-12T00:00:18.388Z") }

# template = {
#     "measurement" : {"mesurevaleur" : }
#     "timestamp": "datemesure",
#     "field" : ["mesure"],
#     "tag" : ["idcapteur","idpiece",]
# }
# [
#     {
#         "measurement": "brushEvents",
#         "tags": {
#             "user": "Carol",
#             "brushId": "6c89f539-71c6-490d-a28d-6c5d84c0ee2f"
#         },
#         "time": "2018-03-28T8:01:00Z",
#         "fields": {
#             "duration": 127
#         }
#     },

# def multiple_log_to_timeserie(jsons, template = None):
#     # TODO : end this function with simple example : with simple template to create 1 time from several in_json documents
#     '''
#     Take a bunch of documents same logs and transform
#     it into a time serie
#     :param jsons : document of document : iterator over several
#     documents
#     :return:
#     '''
#     if template is None:
#         pass
#     else :
#         points = []
#         tm_field = Template()
#         tm_tag = Template()
#         tm_measurement = Template()
#         tm_timestamp = Template()
#         for in_json in jsons:
#             pass
#
# from jinja2 import Template
# if __name__=="__main__":
#     person = {'log': [{"type":"temperature", "value":14}], 'age': 34}
#     print(person.keys())
#     tm = Template("{{doc.0.log.type}}")
#     # tm = Template("My name is {{ per['name'] }} and I am {{ per['age'] }}")
#     msg = tm.render(doc=person)
#
#     print(msg)
def mongodoc_to_influx_list(doc,template=None):
    date, uri, payload = doc
    value = payload.pop("value")
    return {
            "measurement": value,
            "tags": [("uri", uri)],
            "time": date,
            "fields": [
                (key, payload[key]) for key in payload.keys()
            ]
        }


def mongodoc_to_influx(in_json, template=None):
    '''

    :param in_json: dict
    :param template: dict
    {
        "measurement" : "field",
        "time" : "field",
        "tags" : ["field1","field2"],
        "fields" : ["field1","field2"]
    }
    :return: dict
    '''
    if template is not None :
        measurement = in_json[template["measurement"]]
        time = in_json[template["time"]]
        tags = [(dict_field, in_json[dict_field]) for dict_field in template["tags"]]
        fields = [(dict_field, in_json[dict_field]) for dict_field in template["fields"]]
        return {
            "measurement": measurement,
            "tags": tags,
            "time": time,
            "fields": fields
        }
    if "payload" in in_json:
        return {
            "measurement": in_json["payload"]["value_units"],
            "tags": [
                ("subID", in_json["payload"]["subID"]),
                ("input", in_json["payload"]["input"])
            ],
            "time": in_json["date"],
            "fields": [
                ("value", in_json["payload"]["value"])
            ]
        }
    elif "data" in in_json:
        if "payload" in in_json["data"]:
            return {
                "measurement": in_json["data"]["payload"]["value_units"],
                "tags": [
                    ("subID", in_json["data"]["payload"]["subID"]),
                     ("input", in_json["data"]["payload"]["input"])
                ],
                "time": in_json["data"]["date"],
                "fields": [
                    ("value", in_json["data"]["payload"]["value"])
                ]
            }
        else:
            return {}
    else:
        return {}

