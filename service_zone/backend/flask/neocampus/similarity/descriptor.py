# import the necessary packages
import cv2
import time
import math
import numpy as np
from sklearn.cluster import KMeans
from skimage.filters import gabor_kernel
from scipy.stats import kurtosis, entropy
from skimage.feature import greycomatrix, greycoprops, graycomatrix

class Descriptor:

    # Histogram de texture
    def descriptor_texture_hitogramme(self, image):
        """
        Input : path_img
        Output : Vector  : ('mean_color_gray', 'var_color_gray', 'kurtosis_color_gray', 'entropy_color_gray',)
        calcule fréquence des pixels (comprises entre 0 et 255) en échelle de color
        """
        image_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        Vector = []
        dst = cv2.calcHist(image_gray, [0], None, [256], [0, 256])
        Vector.append(np.mean(dst))
        Vector.append(np.var(dst))
        k = kurtosis(dst, axis=0)
        Vector.append(k[0])
        e = entropy(dst)
        Vector.append(e[0])
        return Vector

    # Histogram de couleur
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
        return Vector

    # Dominant color
    def EXTRACT_FEATURS(self, hist, centroids):
        Features = []
        for (percent, color) in zip(hist, centroids):
            color = list(color.flatten())
            color.append(percent * 100)
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
        numLabels = np.arange(0, len(np.unique(labels)) + 1)
        hist, bins = np.histogram(labels, bins=numLabels)
        hist = hist.astype("float")
        hist /= hist.sum()
        Features = self.EXTRACT_FEATURS(hist, centers)
        Flat_Features = [np.round(item, 3) for Sublist_Features in Features for item in Sublist_Features]
        return Flat_Features

    # Matrice de coccurrence
    def descriptor_matix_coccurrence(self, image):
        """
        Input : Image
        Output : Vector of Features : ('dissimilarity','correlation', 'contrast','homogeneity','energy')
        Compute the contrast for GLCMs with distances [1] and angles [0 degrees]
        """
        image_grey = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        Vector = []
        Features = ['dissimilarity', 'correlation', 'contrast', 'homogeneity', 'energy']
        #Greycomatrix = greycomatrix(image_grey, distances=[1], angles=[0], levels=256, symmetric=True, normed=False) #version ==1.0
        Greycomatrix = graycomatrix(image_grey, distances=[1], angles=[0], levels=256, symmetric=True, normed=False)

        for f in Features:
            item = greycoprops(Greycomatrix, f)[0, 0]
            Vector.append(np.round(item, 3))
        return Vector

    # Moment de Hu
    def descriptor_moments_Hu(self, image):
        """
        Input : Image
        Output : Vector  : ('M1', 'M2', 'M3', 'M4', 'M5', 'M6', 'M7')
        calcule fréquence des pixels (comprises entre 0 et 255) en échelle de color
        """
        image_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        image_binary = cv2.threshold(image_gray, 127, 255, cv2.THRESH_BINARY)[1]
        # Calculate Moments
        moments = cv2.moments(image_binary)
        huMoments = cv2.HuMoments(moments).flatten()

        return list(huMoments)

    # SIFT
    def descriptor_sift(self, image_gray):
        """
        Input : Image
        Output : Vector  : (hist1 + hist2 + hist3)
        """
        Vector = []
        # sift = cv2.xfeatures2d.SIFT_create() #opencv-python == 3.0
        sift = cv2.SIFT_create()  # opencv-python > 4.0
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

    # filtrage
    def process(self, img, filters):
        accum = np.zeros_like(img)
        for kern in filters:
            fimg = cv2.filter2D(img, cv2.CV_8UC3, kern)
            np.maximum(accum, fimg, accum)
        return accum

    # Filtres de Gabore
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

    # reduce the vector to 65 caracteristiques
    def reduce_dim(self, vect):
        columns_importances = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '12', '13', '14', '17', '27',
                               '28', '32', '33', '34', '36', '37', '38', '39', '42', '43', '44', '52',
                               '53', '54', '57', '58', '59', '62', '63', '64', '67', '68', '69', '70',
                               '71', '72', '73', '74', '77', '78', '79', '83', '84', '85', '86', '87',
                               '88', '89', '91', '92', '93', '94', '95', '109', '110', '241',
                               '242', '373', '374', '425', '492']
        return [vect[int(i)] for i in columns_importances]

    # Concatination de tous les descripteurs
    def image_query_describe(self, image):
        DTH = self.descriptor_texture_hitogramme(image)
        DMC = self.descriptor_matix_coccurrence(image)
        DFG = self.descriptor_filters_gabore(image)
        DHC = self.descriptor_color_hitogramme(image)
        DCD = self.descriptor_dominant_color(image)
        DSIFT = self.descriptor_sift(image)
        DMH = self.descriptor_moments_Hu(image)
        return self.reduce_dim(DTH + DMC + DFG + DHC + DCD + DSIFT + DMH)