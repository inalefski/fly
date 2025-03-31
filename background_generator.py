import cv2
import numpy  as np
from tkinter.filedialog import askdirectory
import os

dir = askdirectory()

images = [x for x in os.listdir(dir) if x.endswith("png")]

USE_LIMIT = True
IMAGE_LIMIT = 125

background = None

for x in range(0, IMAGE_LIMIT if USE_LIMIT else len(images)):
    if x >= len(images):
        break

    image = cv2.imread(f"{dir}/{images[x]}", cv2.IMREAD_COLOR)

    if x>0:
        background = cv2.max(background, image)
    else:
        background = image

cv2.imwrite("background.png", background)