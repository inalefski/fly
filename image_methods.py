import cv2
import os
from configuration import *

def list_images():
    files = os.listdir(f"./{IMAGE_FOLDER}")

    return [file for file in files if file.endswith(ALLOWED_EXTENSIONS)]

def get_image_info_from_name(image_name: str):
    image_name= image_name.split(".")[0]
    # date, time, image id
    return (image_name[6:16], image_name[17:23], image_name[24:])

def pre_process_image(raw_image: cv2.Mat):
    image = raw_image
    if USE_COLOR_MAX :
        image= cv2.max(image, COLOR_MAX)
    if USE_BLUR:
        image = cv2.blur(image,BLUR_RADIUS)
    return image

def load_image(file_name, use_image_folder=True):
    loaded_image = cv2.imread(f"{IMAGE_FOLDER}/{file_name}" if use_image_folder else file_name, cv2.IMREAD_COLOR)

    if IMAGE_RESIZE_ENABLE:
        return cv2.resize(loaded_image, IMAGE_RESIZE_TO)
    
    return loaded_image
