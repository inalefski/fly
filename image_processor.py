import cv2
import numpy as np
import os
import image_analyzers
import json
import datetime
import csv

from configuration import * 
from image_methods import *
BACKGROUND = pre_process_image(load_image(BACKGROUND_IMAGE, use_image_folder=False))
ANALYZER = image_analyzers.ContourProcessor(BACKGROUND, ARENAS, IMAGE_THRESHOLD, MIN_CONTOUR_SIZE, MAX_CONTOUR_SIZE)

frame_data = []
images = list_images()

loaded_images = []

if ENABLE_TEST_MODE:
    raw_image = load_image(images[TEST_IMAGE_ID])
    pre_image = pre_process_image(raw_image)
    image_data = ("", "","")#get_image_info_from_name(images[TEST_IMAGE_ID])
    background_subtracted = cv2.subtract(BACKGROUND, pre_image)

    raw_image_prev = load_image(images[TEST_IMAGE_ID-1])
    pre_image_prev = pre_process_image(raw_image_prev)
    prev_background_subtracted = cv2.subtract(BACKGROUND, pre_image_prev)

    data_prev, binarized_prev = ANALYZER.process_raw(pre_image_prev)
    frame_prev = ANALYZER.process_image(data_prev, image_data)

    data_curr, binarized_curr = ANALYZER.process_raw(pre_image)
    frame_curr = ANALYZER.process_image(data_curr, image_data)

    moved_contours = ANALYZER.perform_last_frame_analysis(pre_image_prev, pre_image, frame_prev, frame_curr)
    debug = cv2.drawContours(np.copy(raw_image), [fly.contour for arena in frame_curr.arenas for fly in arena.flies if fly.moved == True], -1, (255,0,0), cv2.FILLED)
    debug = cv2.drawContours(debug, [fly.contour for arena in frame_curr.arenas  for fly in arena.flies if fly.moved == False], -1, (0,255,0), cv2.FILLED)

    cv2.imshow("current image", cv2.resize(np.copy(raw_image), TEST_IMAGE_SIZE))
    cv2.imshow("Previous Image", cv2.resize(np.copy(pre_image_prev), TEST_IMAGE_SIZE))
    cv2.imshow("identity", cv2.resize(np.copy(debug), TEST_IMAGE_SIZE))
    cv2.imshow("backround subtracted and binarized", cv2.resize(np.copy(binarized_curr), TEST_IMAGE_SIZE))
    cv2.imshow("BackgroundSubtracted", cv2.resize(np.copy(background_subtracted), TEST_IMAGE_SIZE))
    #cv2.imwrite("Contours.png", debug)
    #cv2.imwrite("Binarized.png",binarized_curr)
    #cv2.imwrite("Background_subtracted.png",background_subtracted)
    #cv2.imwrite("Binarized_Previous.png",binarized_prev)
    #cv2.imwrite("Background_subtracted_Previous.png",prev_background_subtracted)
    cv2.waitKey()
    exit()

if SAVE_DEBUG_IMAGES and not os.path.isdir(DEBUG_IMAGE_OUTPUT_DIR):
    os.mkdir(DEBUG_IMAGE_OUTPUT_DIR)

for id in range(0, len(images)):
    image_name = images[id]

    raw_image = load_image(image_name)
    pre_image = pre_process_image(raw_image)
    image_data = get_image_info_from_name(image_name)

    data, binarized = ANALYZER.process_raw(pre_image)
    frame = ANALYZER.process_image(data, image_data)
    loaded_images.append(pre_image)

    if id > 0:
        moved_contours = ANALYZER.perform_last_frame_analysis(loaded_images[id-1], loaded_images[id], frame_data[id-1], frame)
        # if(len(moved_contours) > 0):
        #     test=cv2.drawContours(np.copy(raw_image), moved_contours, -1, (255,0,255), 1)
        #     cv2.imshow("", test)
        #     cv2.imshow("curr", raw_image)
        #     cv2.imshow("prev", loaded_images[id-1])
        #     cv2.waitKey()

    if SAVE_DEBUG_IMAGES and id < DEBUG_IMAGE_COUNT:
        debug = cv2.drawContours(np.copy(raw_image), [fly.contour for arena in frame.arenas for fly in arena.flies if fly.moved == True], -1, (255,0,0), cv2.FILLED)
        debug = cv2.drawContours(debug, [fly.contour for arena in frame.arenas  for fly in arena.flies if fly.moved == False], -1, (0,255,0), cv2.FILLED)
        cv2.imwrite(f"{DEBUG_IMAGE_OUTPUT_DIR}/{frame.image_id}.png", debug)

    for arena in frame.arenas:
        for fly in arena.flies:
            fly.contour = None

  
    frame_data.append(frame)

if not os.path.isdir(DATA_OUTPUT_DIR):
    os.mkdir(DATA_OUTPUT_DIR)

data_name = f"{DATA_OUTPUT_DIR}/test"
date = datetime.datetime.now()
data_name += "_" + date.strftime("%m-%d-%Y_%H-%M-%S")

json_data_name = data_name + ".json"
csv_data_name = data_name + ".csv"

if DATA_EXPORT_JSON:
    with open(json_data_name, "w") as file:
        json.dump(frame_data, file, indent=4, cls=image_analyzers.FlyEncoder)

if DATA_EXPORT_CSV:
    headers = []

    dict_list = []

    # Each Frame
    frame: image_analyzers.Frame
    for frame in frame_data:
        # Make row for each frame
        frame_output = {}
        frame_dict = frame.__dict__
        # For Each key
        for key in frame_dict:
            # If areans skip because its an object
            if key == "arenas":
                continue

            # Add this key to the frame dict
            frame_output[key] = frame_dict[key]

            # Keep track of all of our headers
            if key not in headers:
                headers.append(key)
        
        # Go through all of frames arenas
        for x in range(0, len(frame_dict['arenas'])):
            arena: image_analyzers.Arena = frame_dict['arenas'][x]
            arena_dict = arena.__dict__
            # Each key
            for key in arena_dict:
                # We can't track fly positions in csv
                if key == "flies" or key == "cluster_sizes":
                    continue
                
                # Prefix the key with arena name eg: 'arena_12' + 'fliesCounted'
                arenaKey = f"arena{(x+1)}_{key}"

                # Add this data to the entire frame
                frame_output[arenaKey] = arena_dict[key]

                # Keep track of headers
                if arenaKey not in headers:
                    headers.append(arenaKey)
        
        # Add to the list
        dict_list.append(frame_output)

    # Open a CSV File
    with open(csv_data_name, "w", newline='') as csvFile:
        # Create CSV Writer, Write Headers and then all rows
        writer = csv.DictWriter(csvFile, fieldnames=headers)
        writer.writeheader()
        writer.writerows(dict_list)
