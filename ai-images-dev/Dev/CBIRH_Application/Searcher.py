# import the necessary packages
import numpy as np
import csv



class Searcher:
    def __init__(self, indexPath):
        # store our index path
        self.indexPath = indexPath

    def search(self, queryFeatures, limit=10):
        # initialize our dictionary of results
        results = {}
        # open the index file for reading
        with open(self.indexPath) as f:
            # initialize the CSV reader
            reader = csv.reader(f)
            # loop over the rows in the index
            for row in reader:
                # parse out the image ID and features, then compute the
                # chi-squared distance between the features in our index
                # and our query features
                # print('---',row)
                features = [float(x.replace(',', '.')) for x in row[1:]]
                d = self.chi2_distance(features, queryFeatures)


                # now that we have the distance between the two feature
                # vectors, we can udpate the results dictionary -- the
                # key is the current image ID in the index and the
                # value is the distance we just computed, representing
                # how 'similar' the image in the index is to our query
                results[row[0]] = d
                # print('len = ',len(results))
            # close the reader
            f.close()
        # sort our results, so that the smaller distances (i.e. the
        # more relevant images are at the front of the list)
        results = sorted([(v, k) for (k, v) in results.items()])
        results = sorted([(v, k) for (v, k) in results if v < 5])

        return results[:limit]

    """    def chi2_distance(self, histA, histB, eps = 1e-10):

        # compute the chi-squared distance
        d = 0.5 * np.sum([((a - b) ** 2) / (a + b + eps) for (a, b) in zip(histA, histB)])
        # return the chi-squared distance
        #print(d)
        return d
        """

    def chi2_distance(self, A, B, eps=1e-10):
        F1_A = A[0:11]
        F2_A = A[12:16]
        F1_B = B[0:11]
        F2_B = B[12:16]
        # compute the chi-squared distance
        d_1 = 0.5 * np.sum([((a - b) ** 2) / (a + b + eps) for (a, b) in zip(F1_A, F1_B)])
        d_2 = 0.5 * np.sum([((a - b) ** 2) / (a + b + eps) for (a, b) in zip(F2_A, F2_B)])
        d = 0.5 * d_1 + 0.5 * d_2
        # return the chi-squared distance
        return d

