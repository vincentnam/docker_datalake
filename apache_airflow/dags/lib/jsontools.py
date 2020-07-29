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
def multiple_log_to_timeserie(jsons, template = None):
    # TODO : end this function with simple example : with simple template to create 1 time from several json documents
    '''
    Take a bunch of documents same logs and transform
    it into a time serie
    :param jsons : document of document : iterator over several
    documents
    :return:
    '''
    if template is None:
        pass
    else :
        points = []
        tm_field = Template()
        tm_tag = Template()
        tm_measurement = Template()
        tm_timestamp = Template()
        for json in jsons:
            pass

from jinja2 import Template
if __name__=="__main__":
    person = {'log': [{"type":"temperature", "value":14}], 'age': 34}
    print(person.keys())
    tm = Template("{{doc.0.log.type}}")
    # tm = Template("My name is {{ per['name'] }} and I am {{ per['age'] }}")
    msg = tm.render(doc=person)

    print(msg)