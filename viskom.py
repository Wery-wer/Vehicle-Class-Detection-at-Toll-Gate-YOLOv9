import streamlit as st
import os
import numpy as np
import tensorflow as tf
from tensorflow.keras.utils import img_to_array
from PIL import Image
import cv2
from ultralytics import YOLO
import time
import shutil
import pandas as pd  

# Load YOLO model
yolo_model = YOLO('Yolov9c(100)lr0.01.pt')

# Load the TensorFlow model
tensorflow_model = tf.keras.models.load_model(r'Adam100Batch32setv2lr0.001.h5')

def prepareImage(image):
    image = tf.image.resize(image, [224, 224])
    imgResult = img_to_array(image)
    imgResult = np.expand_dims(imgResult, axis=0)
    imgResult = imgResult / 255. 
    return imgResult

def save_image_to_directory(img, filename, save_directory, num_boxes):
    if save_directory:
        os.makedirs(save_directory, exist_ok=True)
        full_path = os.path.join(save_directory, filename)
        tf.keras.preprocessing.image.save_img(full_path, img)
        st.write(f"Original image saved to: {save_directory}")
    else:
        st.write(f"Bounding box count {num_boxes} is not handled.")
def update_vehicle_count(vehicle_class):
    if 'vehicle_counts' not in st.session_state:
        st.session_state.vehicle_counts = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}  
    
    
    if vehicle_class in st.session_state.vehicle_counts:
        st.session_state.vehicle_counts[vehicle_class] += 1


def predict(img, filename, i):
    img_np = img.numpy()
    img_np = np.squeeze(img_np)

    # YOLO prediction
    start_time = time.time()
    results = yolo_model.predict(img_np, conf=0.3, save=True)
    end_time = time.time()
    inference_time_yolo = end_time - start_time

    # TensorFlow (ResNet) prediction
    start_time_resnet = time.time()
    imgres = prepareImage(img)
    resultArray = tensorflow_model.predict(imgres)
    end_time_resnet = time.time()
    inference_time_resnet = end_time_resnet - start_time_resnet

    yolo_save_dir = results[0].save_dir
    file_name = "image0.jpg"
    yolo_image_path = os.path.join(yolo_save_dir, file_name)
    img = cv2.imread(yolo_image_path)
    num_boxes = len(results[0].boxes)
    save_directory = None
    if num_boxes == 0:
        imgres = prepareImage(img)
        resultArray = tensorflow_model.predict(imgres)
        answer = np.argmax(resultArray, axis=1)
        if answer is not None:
            index = answer[0]
            update_vehicle_count(index+1)  
            return index
    elif num_boxes == 1:
        imgres = prepareImage(img)
        resultArray = tensorflow_model.predict(imgres)
        answer = np.argmax(resultArray, axis=1)
        if answer is not None:
            index = answer[0]
            update_vehicle_count(index+1)  
            return index
    elif num_boxes == 2:
        imgres = prepareImage(img)
        resultArray = tensorflow_model.predict(imgres)
        answer = np.argmax(resultArray, axis=1)
        if answer is not None:
            index = answer[0]
            update_vehicle_count(index+1)  
            return index
    elif num_boxes == 3:
        update_vehicle_count(3) 
        return(2)
    elif num_boxes == 4:
        update_vehicle_count(4)  
        return(3)
    elif num_boxes >= 5:
        update_vehicle_count(5) 
        return(4)


# Streamlit UI 
st.title("Image Processing with YOLO and TensorFlow Models")

option = st.radio("Select input method:", ("Upload Image", "Use Webcam"))

if option == "Upload Image":
    uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])

    if uploaded_file is not None:
        image = tf.image.decode_image(uploaded_file.read(), channels=3)

        image_np = image.numpy()
        image_pil = Image.fromarray(image_np)

        st.image(image_pil, caption="Uploaded Image", use_column_width=True)
        st.write("")

        if st.button("Process Image"):
            result = predict(image, uploaded_file.name, 0)

            st.write(f"Processed image, result: Class {result+1}")

elif option == "Use Webcam":
    image_file = st.camera_input("Take a picture")

    if image_file is not None:
        image = tf.image.decode_image(image_file.getvalue(), channels=3)

        image_np = image.numpy()
        image_pil = Image.fromarray(image_np)

        st.image(image_pil, caption="Captured Image", use_column_width=True)
        st.write("")
        
        if st.button("Process Image"):
            result = predict(image, "captured_image.jpg", 0)

            st.write(f"Processed image, result: Class {result+1}")

if 'vehicle_counts' in st.session_state:
    st.write("### Detected Vehicle Counts")
    df_counts = pd.DataFrame(list(st.session_state.vehicle_counts.items()), columns=['Class', 'Total Detections'])
    st.table(df_counts)


