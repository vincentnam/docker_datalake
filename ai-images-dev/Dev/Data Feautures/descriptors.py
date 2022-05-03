import os
import cv2 
import time
import math
import numpy as np
import pandas as pd
from skimage.filters import gabor_kernel
from scipy.stats import kurtosis, entropy
from skimage.feature import greycomatrix, greycoprops
from sklearn.cluster import KMeans


class Descriptors:

    def __init__(self, nbr_class, nbr_images):
        self.nbr_class = nbr_class
        self.nbr_images = nbr_images



    def descriprot_texture_hitogramme(self, path_img) :
        """
        Input : path_img

        Output : Vector  : ('mean_color_gray', 'var_color_gray', 'kurtosis_color_gray', 'entropy_color_gray',)

        calcule fréquence des pixels (comprises entre 0 et 255) en échelle de color
        """
        #start = time.time()
        image_gray=cv2.imread (path_img,0)
        Vector = []
        #cv2.calcHist (images, canaux, masque, histSize, plages )
        dst = cv2.calcHist(image_gray, [0], None, [256], [0, 256])
        Vector.append(np.mean(dst))
        Vector.append(np.var(dst))
        k = kurtosis(dst,axis = 0)
        Vector.append(k[0])
        e = entropy(dst)
        Vector.append(e[0])

        #end = time.time()
        #print("[INFO] Applying took {:.2f} seconds".format(end - start))
        return Vector

    def descriprot_color_hitogramme(self,path_img) :
        """
        Input : path_img

        Output : Vector  : ('mean_color_1', 'var_color_1', 'kurtosis_color_1', 'entropy_color_1',
                            'mean_color_2', 'var_color_2', 'kurtosis_color_2', 'entropy_color_2'
                            'mean_color_3', 'var_color_3', 'kurtosis_color_3', 'entropy_color_3')

        calcule fréquence des pixels (comprises entre 0 et 255) en échelle de color
        """
        #start = time.time()
        image_rgb = cv2.cvtColor(cv2.imread(path_img), cv2.COLOR_BGR2RGB)
        Vector = []
        for i, col in enumerate(['b', 'g', 'r']):
            dst = cv2.calcHist(image_rgb, [i], None, [256], [0, 256])
            Vector.append(np.mean(dst))
            Vector.append(np.var(dst))
            k = kurtosis(dst,axis = 0)
            Vector.append(k[0])
            e = entropy(dst)
            Vector.append(e[0])

        #end = time.time()
        #print("[INFO] Applying took {:.2f} seconds".format(end - start))
        return Vector


    def EXTRACT_FEATURS(self, hist,centroids):

        Vector = []
        Features = []
        for (percent, color) in zip(hist, centroids):     
            color = list(color.flatten())        
            color.append(percent*100 )
            Features.append(color)    
            #print("percent :",np.round(percent*100,3),"\tcolor : ",color)
        return Features

    def DOMINANT_COLOR_DESCRIPTOR(self, path_img):
        """
        Input : path_img
        Output : Vector of Features : ('Color_1','Percent_1','Color_2','Percent_2'','Color_3','Percent_3')

        """
        # Convert Image from RGB to CIE LUV
        img_Luv = cv2.cvtColor(cv2.imread(path_img), cv2.COLOR_BGR2LUV)
        pixels = np.float32(img_Luv.reshape(-1, 3))
        # Nuber of class chosen by the elbow method
        n_colors = 3
        # Generate cluster centers using the kmeans() methode of opencv
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 200, .1)
        flags = cv2.KMEANS_RANDOM_CENTERS
        _, labels, centers = cv2.kmeans(pixels, n_colors, None, criteria, 10, flags)
        # Generate the histogram to calculate the percent of each color 
        numLabels = np.arange(0, len(np.unique(labels)) + 1)
        hist, bins = np.histogram(labels, bins = numLabels)
        hist = hist.astype("float")
        hist /= hist.sum()
        
        Features = self.EXTRACT_FEATURS(hist,centers)
        Flat_Features = [np.round(item,3) for Sublist_Features in Features for item in Sublist_Features]

        return Flat_Features

    def DESCRIPTOR_TEXTURE_MATRIX_COCCURRENCE(self, path_img):
        """
        Input : Image gray
        Output : Vector of Features : ('dissimilarity','correlation', 'contrast','homogeneity','energy')
        Compute the contrast for GLCMs with distances [1] and angles [0 degrees]
        """
        #start = time.time()
        image_gray = cv2.imread(path_img,0)
        Vector = []
        Features = ['dissimilarity','correlation', 'contrast','homogeneity','energy']  
        Greycomatrix = greycomatrix(image_gray, distances=[1], angles=[0], levels=256,symmetric=True, normed=False)
        for f in Features:
            item = greycoprops(Greycomatrix, f)[0, 0]
            Vector.append(np.round(item,3))   
        #end = time.time()
        #print("[INFO] Applying took {:.2f} seconds".format(end - start))
        return Vector

    def descriprot_moments_Hu(self, path_img) :
        """
        Input : Image

        Output : Vector  : ('M1', 'M2', 'M3', 'M4', 'M5', 'M6', 'M7')

        calcule fréquence des pixels (comprises entre 0 et 255) en échelle de color
        """
        #start = time.time()
        Vector = []
        image_gray = cv2.imread (path_img,0)
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

    def descriprot_sift(self, path_img) :
        """
        Input : Image

        Output : Vector  : (hist1 + hist2 + hist3)


        """
        #start = time.time()
        Vector = []
        image_gray = cv2.imread (path_img,0)
        sift = cv2.xfeatures2d.SIFT_create()
        kp, des = sift.detectAndCompute(image_gray,None)
        matrix = []
        for k in range(0,len(kp)):
            kp_des = []
            kp_des.append(kp[k].pt[0])
            kp_des.append(kp[k].pt[1])
            kp_des.append(kp[k].angle)
            kp_des.append(kp[k].octave)
            kp_des.extend(des[k])
            matrix.append(kp_des)
        new_des = np.asarray(matrix, dtype=float, order=None)
        kmeans = KMeans(n_clusters=6, init='k-means++', random_state=0).fit(new_des)
        Vector.extend(kmeans.cluster_centers_[0])
        Vector.extend(kmeans.cluster_centers_[1])
        Vector.extend(kmeans.cluster_centers_[2])

        #print("[INFO] Applying took {:.2f} seconds".format(end - start))
        return Vector
    
    # prepare filter bank kernels
    def build_filters(self):
        filters = []
        names = []
        for theta in range(5):
            name_theta = f'theta = {theta}*pi/4 et '
            theta = theta / 4. * np.pi
            for freq in (4,8,16,32,64):
                name_freq = f'freq ={freq}'
                frequency = (math.sqrt(2)*freq) / 256
                kernel = np.real(gabor_kernel(frequency, theta=theta))
                filters.append(kernel)
                names.append(name_theta + name_freq)
        return filters, names

    def process(self,img, filters):
        accum = np.zeros_like(img)
        for kern in filters:
            fimg = cv2.filter2D(img, cv2.CV_8UC3, kern)
            np.maximum(accum, fimg, accum)
        return accum
    
    def descriprot_filter_gabor(self, path_img) :
        """
        Input : Image

        Output : Vector  : (list_moyenne + list_var + list_energy)


        """
        #start = time.time()
        Vector = []
        image_gray = cv2.imread (path_img,0)
        res = []
        m = []
        e = []
        v = []
        kernels, names = self.build_filters()
        for i in range(0,len(kernels)):
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

        #print("[INFO] Applying took {:.2f} seconds".format(end - start))
        return Vector
    
    def create_data_feautures_2_descriptors(self, PATH_LIST,columns,path_data_csv, name_file, vector_1, vector_2):
        """
        Input : 
            *PATH_LIST : list Image Directory Path
            *columns : header of data
            *path_data_csv : CSV File Directory Path
            *name_file : The name of the file (Data_Features)
            *CSV File "The descriptor database " save in directory 'Data_CSV' 
            *vector_1 : first descriptor (Texture / couleur / forme)
            *vector_2 : first descriptor (Texture / couleur / forme)
        Output : 
            *dataframe :

        """
        start = time.time()
        df = pd.DataFrame(columns = columns)
        for f in range(0,int(self.nbr_class)):
            for i in range(0,int(self.nbr_images /self.nbr_class)):
                ligne = []
                path_img = os.path.join(PATH_LIST[f],os.listdir(PATH_LIST[f])[i])
                name_img = os.listdir(PATH_LIST[f])[i].split('.')[0]
                ligne.append(name_img)

                ligne.extend(vector_1(path_img))
                ligne.extend(vector_2(path_img))

                ligne.append(f)

                # Using append to add the list to DataFrame
                df = df.append(pd.DataFrame([ligne], columns=columns), ignore_index=True)
        if os.path.isfile(os.path.join(path_data_csv,name_file))==False:
            df.to_csv(os.path.join(path_data_csv,name_file), header=True, index = False, sep =',')
        else : 
            os.remove(os.path.join(path_data_csv,name_file))
            df.to_csv(os.path.join(path_data_csv,name_file), header=True, index = False, sep =',')
        end = time.time()
        print("[INFO] Applying took {:.2f} seconds".format(end - start))
        return df
    
    def create_data_feautures_2_descriptors_without_header(self, PATH_LIST,path_data_csv, name_file, vector_1, vector_2):
        """
        Input : 
            *PATH_LIST : list Image Directory Path
            *columns : header of data
            *path_data_csv : CSV File Directory Path
            *name_file : The name of the file (Data_Features)
            *CSV File "The descriptor database " save in directory 'Data_CSV' 
            *vector_1 : first descriptor (Texture / couleur / forme)
            *vector_2 : first descriptor (Texture / couleur / forme)
        Output : 
            *dataframe :

        """
        start = time.time()
        df = pd.DataFrame()
        for f in range(0,int(self.nbr_class)):
            for i in range(0,int(self.nbr_images /self.nbr_class)):
                ligne = []
                path_img = os.path.join(PATH_LIST[f],os.listdir(PATH_LIST[f])[i])
                name_img = os.listdir(PATH_LIST[f])[i].split('.')[0]
                ligne.append(name_img)

                ligne.extend(vector_1(path_img))
                ligne.extend(vector_2(path_img))

                ligne.append(f)

                # Using append to add the list to DataFrame
                df = df.append(pd.DataFrame([ligne]), ignore_index=True)
        if os.path.isfile(os.path.join(path_data_csv,name_file))==False:
            df.to_csv(os.path.join(path_data_csv,name_file), index = False, sep =',')
        else : 
            os.remove(os.path.join(path_data_csv,name_file))
            df.to_csv(os.path.join(path_data_csv,name_file),  index = False, sep =',')
        end = time.time()
        print("[INFO] Applying took {:.2f} seconds".format(end - start))
        return df

    def create_data_feautures_3_descriptors(self, PATH_LIST,columns,path_data_csv, name_file, vector_1, vector_2,vector_3):
        """
        Input : 
            *PATH_LIST : list Image Directory Path
            *columns : header of data
            *path_data_csv : CSV File Directory Path
            *name_file : The name of the file (Data_Features)
            *CSV File "The descriptor database " save in directory 'Data_CSV' 
            *vector_1 : first descriptor (Texture / couleur / forme)
            *vector_2 : first descriptor (Texture / couleur / forme)
            *vector_3 : first descriptor (Texture / couleur / forme)
        Output : 
            *dataframe

        """
        start = time.time()
        df = pd.DataFrame(columns = columns)
        for f in range(0,int(self.nbr_class)):
            for i in range(0,int(self.nbr_images / self.nbr_class)):
                ligne = []
                path_img = os.path.join(PATH_LIST[f],os.listdir(PATH_LIST[f])[i])
                name_img = os.listdir(PATH_LIST[f])[i].split('.')[0]
                ligne.append(name_img)

                ligne.extend(vector_1(path_img))
                ligne.extend(vector_2(path_img))
                ligne.extend(vector_3(path_img))

                ligne.append(f)

                # Using append to add the list to DataFrame
                df = df.append(pd.DataFrame([ligne], columns=columns), ignore_index=True)
        if os.path.isfile(os.path.join(path_data_csv,name_file))==False:
            df.to_csv(os.path.join(path_data_csv,name_file), header=True, index = False, sep =',')
        else :
            os.remove(os.path.join(path_data_csv,name_file))
            df.to_csv(os.path.join(path_data_csv,name_file), header=True, index = False, sep =',')
        end = time.time()
        print("[INFO] Applying took {:.2f} seconds".format(end - start))
        return df
    
    def create_data_feautures_3_descriptors_without_header(self, PATH_LIST,path_data_csv, name_file, vector_1, vector_2,vector_3):
        """
        Input : 
            *PATH_LIST : list Image Directory Path
            *columns : header of data
            *path_data_csv : CSV File Directory Path
            *name_file : The name of the file (Data_Features)
            *CSV File "The descriptor database " save in directory 'Data_CSV' 
            *vector_1 : first descriptor (Texture / couleur / forme)
            *vector_2 : first descriptor (Texture / couleur / forme)
            *vector_3 : first descriptor (Texture / couleur / forme)
        Output : 
            *dataframe

        """
        start = time.time()
        df = pd.DataFrame()
        for f in range(0,int(self.nbr_class)):
            for i in range(0,int(self.nbr_images / self.nbr_class)):
                ligne = []
                path_img = os.path.join(PATH_LIST[f],os.listdir(PATH_LIST[f])[i])
                name_img = os.listdir(PATH_LIST[f])[i].split('.')[0]
                ligne.append(name_img)

                ligne.extend(vector_1(path_img))
                ligne.extend(vector_2(path_img))
                ligne.extend(vector_3(path_img))

                ligne.append(f)

                # Using append to add the list to DataFrame
                df = df.append(pd.DataFrame([ligne],), ignore_index=True)
        if os.path.isfile(os.path.join(path_data_csv,name_file))==False:
            df.to_csv(os.path.join(path_data_csv,name_file), header=True, index = False, sep =',')
        else :
            os.remove(os.path.join(path_data_csv,name_file))
            df.to_csv(os.path.join(path_data_csv,name_file), header=True, index = False, sep =',')
        end = time.time()
        print("[INFO] Applying took {:.2f} seconds".format(end - start))
        return df 
    
    def create_data_feautures_all_descriptors_without_header(self, PATH_LIST,path_data_csv, name_file):
        """
        Input : 
            *PATH_LIST : list Image Directory Path
            *path_data_csv : CSV File Directory Path
            *name_file : The name of the file (Data_Features)
        Output : 
            *dataframe : TH_GCM_FG_CH_DCD_SIFT_HM

        """
        start = time.time()
        df = pd.DataFrame()
        for f in range(0,int(self.nbr_class)):
            for i in range(0,int(self.nbr_images / self.nbr_class)):
                ligne = []
                path_img = os.path.join(PATH_LIST[f],os.listdir(PATH_LIST[f])[i])
                name_img = os.listdir(PATH_LIST[f])[i].split('.')[0]
                ligne.append(name_img)

                ligne.extend(self.descriprot_texture_hitogramme(path_img))
                ligne.extend(self.DESCRIPTOR_TEXTURE_MATRIX_COCCURRENCE(path_img))
                ligne.extend(self.descriprot_filter_gabor(path_img))

                ligne.extend(self.descriprot_color_hitogramme(path_img))
                ligne.extend(self.DOMINANT_COLOR_DESCRIPTOR(path_img))
                
                ligne.extend(self.descriprot_sift(path_img))
                ligne.extend(self.descriprot_moments_Hu(path_img))

                ligne.append(f)

                # Using append to add the list to DataFrame
                df = df.append(pd.DataFrame([ligne],), ignore_index=True)
        if os.path.isfile(os.path.join(path_data_csv,name_file))==False:
            df.to_csv(os.path.join(path_data_csv,name_file), header=True, index = False, sep =',')
        else :
            os.remove(os.path.join(path_data_csv,name_file))
            df.to_csv(os.path.join(path_data_csv,name_file), header=True, index = False, sep =',')
        end = time.time()
        print("[INFO] Applying took {:.2f} seconds".format(end - start))
        return df 