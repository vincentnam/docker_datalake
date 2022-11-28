import io
import requests
from PIL import Image
import streamlit as st
import matplotlib.pyplot as plt

def desplay_images(data):
    rows = 5
    fig1 = plt.figure(figsize=(25, 25))
    for num, img in enumerate(data):
        image_encode = eval(img[1])
        image = Image.open(io.BytesIO(image_encode))
        plt.subplot(rows, 5, num + 1)
        plt.axis('off')
        plt.imshow(image)
    st.pyplot(fig1)

col1, col2 = st.columns([2, 5])
image_file = col2.file_uploader("Choose an image")
session = requests.Session()
menu = ["Similarity", "Classification"]
choice = st.sidebar.selectbox("Menu", menu)
if choice == "Similarity":
    if image_file is not None:
        files = {"file": image_file.getvalue()}
        col2.subheader("Query Image")
        img = Image.open(image_file)
        col2.image(img, width=150)
        data = requests.post(f"http://127.0.0.1:5000/similarity", files=files)
        if data:
            data = data.json()
            col2.subheader("Result : Limit 10 Images")
            desplay_images(data[0])
        else:
            st.error("[Error] : Data request is empty")