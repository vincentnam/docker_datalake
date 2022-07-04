# import the necessary packages
import cv2
import time
import math
import numpy as np
from sklearn.cluster import KMeans
from skimage.filters import gabor_kernel
from scipy.stats import kurtosis, entropy
from skimage.feature import greycomatrix, greycoprops

class Descriptor:

    #Histogramme de texture
    def descriptor_texture_hitogramme(self, image) :
        """
        Input : path_img
        Output : Vector  : ('mean_color_gray', 'var_color_gray', 'kurtosis_color_gray', 'entropy_color_gray',)
        calcule fréquence des pixels (comprises entre 0 et 255) en échelle de color
        """
        image_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        Vector = []
        #cv2.calcHist (images, canaux, masque, histSize, plages )
        dst = cv2.calcHist(image_gray, [0], None, [256], [0, 256])
        Vector.append(np.mean(dst))
        Vector.append(np.var(dst))
        k = kurtosis(dst,axis = 0)
        Vector.append(k[0])
        e = entropy(dst)
        Vector.append(e[0])
        return Vector
    #Histogramme de couleur
    def descriptor_color_hitogramme(self, image):
        """
        Input : Image
        Output : Vector  : ('mean_color_1', 'var_color_1', 'kurtosis_color_1', 'entropy_color_1',
                            'mean_color_2', 'var_color_2', 'kurtosis_color_2', 'entropy_color_2'
                            'mean_color_3', 'var_color_3', 'kurtosis_color_3', 'entropy_color_3')
        calcule fréquence des pixels (comprises entre 0 et 255) en échelle de color
        """
        Vector = []
        for i, col in enumerate(['b', 'g', 'r']):
            dst = cv2.calcHist(image, [i], None, [256], [0, 256])
            Vector.append(np.mean(dst))
            Vector.append(np.var(dst))
            k = kurtosis(dst, axis=0)
            Vector.append(k[0])
            e = entropy(dst)
            Vector.append(e[0])
        end = time.time()
        # print("[INFO] Applying took {:.2f} seconds".format(end - start))
        return Vector
    #Couleur dominante
    def EXTRACT_FEATURS(self, hist,centroids):
        Features = []
        for (percent, color) in zip(hist, centroids):
            color = list(color.flatten())
            color.append(percent*100 )
            Features.append(color)
        return Features
    def descriptor_dominant_color(self, img):
        """
        Input : Image
        Output : Vector of Features : ('Color_1','Percent_1','Color_2','Percent_2'','Color_3','Percent_3')
        """
        # Convert Image from RGB to CIE LUV
        img_Luv = cv2.cvtColor(img, cv2.COLOR_BGR2LUV)
        pixels = np.float32(img_Luv.reshape(-1, 3))
        # Nuber of class chosen by the elbow method
        n_colors = 3
        # Generate cluster centers using the kmeans() methode of opencv
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 200, .1)
        flags = cv2.KMEANS_RANDOM_CENTERS
        cv2.KMEANS_USE_INITIAL_LABELS
        # print(flags)
        _, labels, centers = cv2.kmeans(pixels, n_colors, None, criteria, 10, 2)
        # Generate the histogram to calculate the percent of each color
        # print('centers',centers)
        numLabels = np.arange(0, len(np.unique(labels)) + 1)
        hist, bins = np.histogram(labels, bins=numLabels)
        hist = hist.astype("float")
        hist /= hist.sum()
        Features = self.EXTRACT_FEATURS(hist, centers)
        Flat_Features = [np.round(item, 3) for Sublist_Features in Features for item in Sublist_Features]
        return Flat_Features
    #Matrice de coccurrence
    def descriptor_matix_coccurrence(self, image):
        """
        Input : Image
        Output : Vector of Features : ('dissimilarity','correlation', 'contrast','homogeneity','energy')
        Compute the contrast for GLCMs with distances [1] and angles [0 degrees]
        """
        image_grey = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        Vector = []
        Features = ['dissimilarity', 'correlation', 'contrast', 'homogeneity', 'energy']
        Greycomatrix = greycomatrix(image_grey, distances=[1], angles=[0], levels=256, symmetric=True, normed=False)
        for f in Features:
            item = greycoprops(Greycomatrix, f)[0, 0]
            Vector.append(np.round(item, 3))
            # end = time.time()
        # print("[INFO] Applying took {:.2f} seconds".format(end - start))
        return Vector
    #Moment de Hu
    def descriptor_moments_Hu(self, image) :
        """
        Input : Image
        Output : Vector  : ('M1', 'M2', 'M3', 'M4', 'M5', 'M6', 'M7')
        calcule fréquence des pixels (comprises entre 0 et 255) en échelle de color
        """
        #start = time.time()
        Vector = []
        image_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        image_binary = cv2.threshold(image_gray, 127, 255, cv2.THRESH_BINARY)[1]
        # Calculate Moments
        moments = cv2.moments(image_binary)
        # Calculate Hu Moments
        huMoments = cv2.HuMoments(moments)
        # Log scale hu moments
        for i in range(0,7):
           Vector.append(-1* math.copysign(1.0, huMoments[i]) * math.log10(abs(huMoments[i])))
        #end = time.time()
        #print("[INFO] Applying took {:.2f} seconds".format(end - start))
        return Vector
    #SIFT
    def descriptor_sift(self, image_gray):
        """
        Input : Image
        Output : Vector  : (hist1 + hist2 + hist3)

        """
        # start = time.time()
        Vector = []
        sift = cv2.xfeatures2d.SIFT_create()
        kp, des = sift.detectAndCompute(image_gray, None)
        matrix = []
        for k in range(0, len(kp)):
            kp_des = []
            kp_des.append(kp[k].pt[0])
            kp_des.append(kp[k].pt[1])
            kp_des.append(kp[k].angle)
            kp_des.append(kp[k].octave)
            kp_des.extend(des[k])
            matrix.append(kp_des)
        new_des = np.asarray(matrix, dtype=float, order=None)
        kmeans = KMeans(n_clusters=3, init='k-means++', random_state=0).fit(new_des)
        Vector.extend(kmeans.cluster_centers_[0])
        Vector.extend(kmeans.cluster_centers_[1])
        Vector.extend(kmeans.cluster_centers_[2])
        # print("[INFO] Applying took {:.2f} seconds".format(end - start))
        return Vector
    ## Filtres de Gabore
     # prepare filter bank kernels
    def build_filters(self):
        filters = []
        names = []
        for theta in range(5):
            name_theta = f'theta = {theta}*pi/4 et '
            theta = theta / 4. * np.pi
            for freq in (4, 8, 16, 32, 64):
                name_freq = f'freq ={freq}'
                frequency = (math.sqrt(2) * freq) / 256
                kernel = np.real(gabor_kernel(frequency, theta=theta))
                filters.append(kernel)
                names.append(name_theta + name_freq)
        return filters, names

     #filtrage
    def process(self,img, filters):
        accum = np.zeros_like(img)
        for kern in filters:
            fimg = cv2.filter2D(img, cv2.CV_8UC3, kern)
            np.maximum(accum, fimg, accum)
        return accum
     #Filtres de Gabore
    def descriptor_filters_gabore(self, image):
        """
        Input : Image
        Output : Vector  : (list_moyenne + list_var + list_energy)
        """
        Vector = []
        image_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        res = []
        m = []
        e = []
        v = []
        kernels, names = self.build_filters()
        for i in range(0, len(kernels)):
            res1 = self.process(image_gray, kernels[i])
            res.append(np.asarray(res1))
        output = np.asarray(res)
        for i in range(len(output)):
            m.append(output[i].mean())
            v.append(output[i].var())
            e.append(output[i].sum())
        Vector.extend(m)
        Vector.extend(v)
        Vector.extend(e)
        return Vector
    #Concatenetion de deuc descripteirs
    def describe_image_query(self,image):
        #image_grey = cv2.imread(imagePath, 0)
        #image_grey = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        #image = cv2.imread(imagePath)
        #img_color = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        # describe the image
        # features_1 = self.describe(image)
        #features_1 = self.DOMINANT_COLOR_DESCRIPTOR(image)
        features_1 = self.descriptor_color_hitogramme(image)
        features_2 = self.descriptor_matix_coccurrence(image)
        return features_1+features_2
    #Concatination de tous les descripteurs
    def image_query_describe(self,image):

        DTH =self.descriptor_texture_hitogramme(image)
        DMC=self.descriptor_matix_coccurrence(image)
        DFG = self.descriptor_filters_gabore(image)
        DHC = self.descriptor_color_hitogramme(image)
        DCD = self.descriptor_dominant_color(image)
        DSIFT = self.descriptor_sift(image)
        DMH = self.descriptor_moments_Hu(   image)
        return DTH+DMC+DFG+DHC+DCD+DSIFT+DMH


    """
    def histogram(self, image, mask):
        # extract a 3D color histogram from the masked region of the
        # image, using the supplied number of bins per channel
        hist = cv2.calcHist([image], [0, 1, 2], mask, (8, 12, 3),
                            [0, 180, 0, 256, 0, 256])
        # normalize the histogram if we are using OpenCV 2.4
        if imutils.is_cv2():
            hist = cv2.normalize(hist).flatten()
        # otherwise handle for OpenCV 3+
        else:
            hist = cv2.normalize(hist, hist).flatten()
        # return the histogram
        return hist
    """
    """
    def describe(self, image):
        # convert the image to the HSV color space and initialize
        # the features used to quantify the image
        image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        features = []
        # grab the dimensions and compute the center of the image
        (h, w) = image.shape[:2]
        (cX, cY) = (int(w * 0.5), int(h * 0.5))
        # divide the image into four rectangles/segments (top-left,
        # top-right, bottom-right, bottom-left)
        segments = [(0, cX, 0, cY), (cX, w, 0, cY), (cX, w, cY, h), (0, cX, cY, h)]
        # construct an elliptical mask representing the center of the
        # image
        (axesX, axesY) = (int(w * 0.75) // 2, int(h * 0.75) // 2)
        ellipMask = np.zeros(image.shape[:2], dtype="uint8")
        cv2.ellipse(ellipMask, (cX, cY), (axesX, axesY), 0, 0, 360, 255, -1)
        # loop over the segments
        for (startX, endX, startY, endY) in segments:
            # construct a mask for each corner of the image, subtracting
            # the elliptical center from it
            cornerMask = np.zeros(image.shape[:2], dtype="uint8")
            cv2.rectangle(cornerMask, (startX, startY), (endX, endY), 255, -1)
            cornerMask = cv2.subtract(cornerMask, ellipMask)
            # extract a color histogram from the image, then update the
            # feature vector
            hist = self.histogram(image, cornerMask)
            features.extend(hist)
        # extract a color histogram from the elliptical region and
        # update the feature vector
        hist = self.histogram(image, ellipMask)
        features.extend(hist)
        # return the feature vector
        return features
    """
    """
    def EXTRACT_FEATURS(self, hist, centroids):

        Vector = []
        Features = []
        for (percent, color) in zip(hist, centroids):
            color = list(color.flatten())
            color = [np.round(item, 2) for item in color]
            color.append(np.round(percent * 100, 3))
            Features.append(color)
            # print("percent :",np.round(percent*100,3),"\tcolor : ",color)
        return Features
    """