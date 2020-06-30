# from neo4j import GraphDatabase
# import pandas as pd
# import pymongo
# import json
# class Neo4jIntegrator():
#     def __init__(self, uri, user, password):
#         self.driver = GraphDatabase.driver(uri, auth=(user, password))
#
#     def close(self):
#         self.driver.close()
#
#     def insert_image(self, metadata):
#         """
#         :param metadata:
#         :return:
#         """
#         req = "MERGE (i1:IMAGE {swift_id :" + metadata["swift_object_id"] + "}) "
#
#         main_node_list = []
#         second_node_list = []
#         aut = 0
#         for obj in metadata["main_object"]:
#             # A ENLEVER
#             if obj != "]" and obj != "[":
#                 id = "a" + str(aut)
#                 req += "MERGE ( " + id + " :OBJECT {type:\"" + obj + "\"}) "
#                 main_node_list.append(str(aut))
#                 aut += 1
#         for obj in metadata["secondary_object"]:
#             if obj != "]" and obj != "[":
#                 id = "a" + str(aut)
#                 req += "MERGE ( " + id + " :OBJECT {type:\"" + obj + "\"}) "
#                 second_node_list.append(str(aut))
#                 aut += 1
#         for nodes in main_node_list:
#             req += "MERGE (i1)-[:SUBJECT]->(" + "a" + str(nodes) + ") "
#
#         for nodes in second_node_list:
#             req += "MERGE (i1)-[:CONTAINS]->(" + "a" + str(nodes) + ") "
#
#         driver = GraphDatabase.driver("neo4j://localhost:7687",
#                                       auth=("test", "test"))
#
#         self.driver.session().run(req)
#
# rep = pymongo.MongoClient("127.0.0.1:27017").swift.mygates.find_one()
# # data_df = pd.read_csv("/data/python-project/docker_datalake/dataset/mygates/subset.csv", sep=";")
# # # print(data_df)
# # print(rep)
# # # print(data_df.iloc[1])
# #
# # print(req)
# neo4j_integ = Neo4jIntegrator("neo4j://localhost:7687", "test", "test")
# neo4j_integ.insert_image(rep)

###

# type_dict = { "image/jpeg":"jpeg_data" , None:"not_handled"}
# callable_dict = {"jpeg_data" : ["jpeg_data"], "not_handled": ["not_handled"] }
# # run_this_first >> branch_op
#
# for dtype in type_dict:
#     pipeline = []
#     print(dtype)
#     for ope in callable_dict[type_dict[dtype]]:
#         print(type(ope))
#         print(callable_dict["jpeg_data"])
#         print(type_dict[dtype])
# #
def jpeg_data():
    pass

def not_handled():
    pass
callable_dict = {"jpeg_data": [jpeg_data],
                 "not_handled": [jpeg_data, not_handled, jpeg_data,
                                 not_handled]}
# run_this_first >> branch_op
type_dict = { "image/jpeg":"jpeg_data" , None:"not_handled"}
pipeline = []
aux = 0
for data_type in type_dict:
    sub_pipe = []
    for ope in callable_dict[type_dict[data_type]]:

        sub_pipe.append( "coucou" )
        aux = aux + 1
    pipeline.append(sub_pipe)
print(pipeline)
# for list in pipeline:
#     chain(branch_op, list, join)