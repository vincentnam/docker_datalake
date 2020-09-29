from neo4j import GraphDatabase

import json


class Neo4jIntegrator:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user,password))


    def close(self):
        self.driver.close()


    # TODO : Refactor this method name
    def insert_image(self, doc):
        """
        :param metadata:
        :return:
        """
        #TODO : parse string to get python object not string
        metadata = doc["other_data"]["image_content"]
        with self.driver.session() as session:
            req = "MERGE (i1:IMAGE {swift_id :" + metadata["swift_object_id"] + "}) "

            main_node_list = []
            second_node_list = []
            aut = 0
            if "main_object" in metadata :
                for obj in metadata["main_object"]:
                    # A ENLEVER
                    if obj != "]" and obj != "[":
                        id = "a" + str(aut)
                        req += "MERGE ( " + id + " :OBJECT {type:\"" + obj + "\"}) "
                        main_node_list.append(str(aut))
                        aut += 1
            if "secondary_object" in metadata:
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

            session.run(req)

            self.print_all()

    def print_all(self):
        with self.driver.session() as session:
            res = session.run("MATCH (a) RETURN a")
            for i in res :
                print(i)
    # def __enter__(self):
    #     '''
    #     Connect to the database.
    #     '''
    #     return self.driver
    #
    # def __exit__(self, exc_type, exc_val, exc_tb):
    #     '''
    #     Close connection at the end of the "with" clause
    #     '''
    #     self.driver.close()