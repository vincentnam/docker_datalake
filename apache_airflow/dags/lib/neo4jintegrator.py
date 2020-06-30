from neo4j import GraphDatabase
import pandas as pd
import pymongo
import json


class Neo4jIntegrator:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()


    # TODO : Refactor this method name
    def insert_image(self, metadata):
        """
        :param metadata:
        :return:
        """
        req = "MERGE (i1:IMAGE {swift_id :" + metadata["swift_object_id"] + "}) "

        main_node_list = []
        second_node_list = []
        aut = 0
        for obj in metadata["main_object"]:
            # A ENLEVER
            if obj != "]" and obj != "[":
                id = "a" + str(aut)
                req += "MERGE ( " + id + " :OBJECT {type:\"" + obj + "\"}) "
                main_node_list.append(str(aut))
                aut += 1
        for obj in metadata["secondary_object"]:
            if obj != "]" and obj != "[":
                id = "a" + str(aut)
                req += "MERGE ( " + id + " :OBJECT {type:\"" + obj + "\"}) "
                second_node_list.append(str(aut))
                aut += 1
        for nodes in main_node_list:
            req += "MERGE (i1)-[:SUBJECT]->(" + "a" + str(nodes) + ") "

        for nodes in second_node_list:
            req += "MERGE (i1)-[:CONTAINS]->(" + "a" + str(nodes) + ") "


        self.driver.session().run(req)