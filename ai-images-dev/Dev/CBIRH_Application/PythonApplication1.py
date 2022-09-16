# import the necessary packages
import cv2
import time
import numpy as np
from PIL import Image
import Searcher as sr
import streamlit as st
import Descriptor as dc
import Classification as cl
import matplotlib.pyplot as plt

class AppCBIRH:

    def load_image(self, image_file):
        img = Image.open(image_file)
        cv_img = cv2.cvtColor(np.asarray(img), cv2.COLOR_BGR2RGB)
        return img,cv_img

    def desplay_images(self,Images):
        rows = 5
        fig1 = plt.figure(figsize=(25, 25))
        for num, img in enumerate(Images):
            plt.subplot(rows, 5, num + 1)
            plt.axis('off')
            plt.imshow(self.load_image(img[1])[0])
        st.pyplot(fig1)

    def menu(self):
        col1, col2 = st.columns([2, 5])
        image_file = col2.file_uploader("")
        app = AppCBIRH()
        descriptor = dc.Descriptor()
        classification = cl.Classification()
        menu = ["Similarity", "Classification"]
        choice = st.sidebar.selectbox("Menu", menu)
        # similiraty
        if choice == "Similarity":
            col1.subheader("Similarity")
            if image_file is not None:
                # To See details
                col2.subheader("Query Image")
                col2.image(app.load_image(image_file)[0], width=250)
                search = sr.Searcher('dataset_index_65.csv')
                start = time.time()
                features = descriptor.image_query_describe(app.load_image(image_file)[1])
                Images = search.search(features)

            result = col1.button('Search Similarity')
            if result:
                    try:
                        col2.subheader("Result : Limit 10 Images")
                        if len(Images)==0:
                            col2.subheader("0 Matches")
                            end = time.time()
                            st.write("[INFO] Applying took {:.2f} seconds".format(end - start))
                        else:
                           app.desplay_images(Images)
                           end = time.time()
                           st.write("[INFO] Applying took {:.2f} seconds".format(end - start))
                    except UnboundLocalError:
                        st.write('Choose an image please !')
        #Classification
        elif choice == "Classification":
            col1.subheader("Classification")
            if image_file is not None:
                col2.subheader("Query Image")
                col2.image(app.load_image(image_file)[0], width=250)
                #col2.image(decode_img, width=250)
                start = time.time()
                features = descriptor.image_query_describe(app.load_image(image_file)[1])
                label = classification.get_predect(features)
                print("label :",label)
                nameofclass = classification.get_key(label)
                end = time.time()
                print("[INFO] Applying took {:.2f} seconds".format(end - start))
                st.write("[INFO] Applying took {:.2f} seconds".format(end - start))
                col2.subheader('Classe : '+nameofclass)

    #def front(self):
        #st.markdown("<h1 style='text-align: center; color: red;'>DataLakeEye</h1>", unsafe_allow_html=True)

def main():
    app = AppCBIRH()
    print()
    #app.front()
    app.menu()


st.set_page_config(
    page_title="DataLakeEye",
    page_icon="Logo/eye.png",
    layout="wide",
    initial_sidebar_state="expanded")

if __name__ == '__main__':
	main()
#-m streamlit