import numpy as np
from joblib import load


class Classification:
    def __init__(self):
        self.classe = {'CAR' : 0, 'CAT' : 1, 'DOG' : 2, 'FRUIT' : 3, 'PERSON':4}
        #self.model = load("RandomForeastModel_0.joblib")
        self.model = load("RandomForeast_Model_65.joblib")



    def get_key(self,val):
        for key, value in self.classe.items():
             if val == value:
                return key

    def get_predect(self,query_image):
        qi = np.array(query_image).reshape(1, -1)
        print(qi.shape)
        return self.model.predict(qi)