import image_analyzers
import numpy as np
import statistics
import time
from configuration import *
from image_methods import *

CHECKER_MIN_CONTOUR_SIZE = 1
CHECKER_MAX_CONTOUR_SIZE = 2500
CHECKER_TEST_IMAGE_ID = 0

CHECKER_SHOW_INDIVIDUAL_FLY_SIZES = True

KEY_PRESS_MAX_CHANGE_AMOUNT = 50
KEY_PRESS_MIN_CHANGE_AMOUNT = 5

BACKGROUND = pre_process_image(load_image(BACKGROUND_IMAGE, use_image_folder=False))

images = list_images()

while True:
    ANALYZER = image_analyzers.ContourProcessor(BACKGROUND, ARENAS, IMAGE_THRESHOLD, CHECKER_MIN_CONTOUR_SIZE, CHECKER_MAX_CONTOUR_SIZE)
    image = load_image(images[CHECKER_TEST_IMAGE_ID])
    pre_image = pre_process_image(image)
    image_data = ("","","")

    contours, binarized = ANALYZER.process_raw(pre_image)
    frame = ANALYZER.process_image(contours, image_data)

    debug = cv2.drawContours(np.copy(image), [fly.contour for arena in frame.arenas for fly in arena.flies], -1, (255,0,0), cv2.FILLED)

    average_contour_size = statistics.mean([fly.size for arena in frame.arenas for fly in arena.flies])

    print(f"Current Average Contour Size: {average_contour_size}")

    debug = cv2.putText(debug, f"Press A/D to change Max Contour Size. Press Q/E to change Min Contour Size", (10,np.shape(image)[0]-25), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 2, cv2.LINE_AA)
    debug = cv2.putText(debug, f"Max Contour Size: {CHECKER_MAX_CONTOUR_SIZE}", (10,30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 2, cv2.LINE_AA)
    debug = cv2.putText(debug, f"Min Contour Size: {CHECKER_MIN_CONTOUR_SIZE}", (10,90), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 2, cv2.LINE_AA)
    debug = cv2.putText(debug, f"Mean Contour Size: {average_contour_size:.2f}", (10,140), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 2, cv2.LINE_AA)

    if CHECKER_SHOW_INDIVIDUAL_FLY_SIZES:
        for arena in frame.arenas:
            for fly in arena.flies:
                fly: image_analyzers.Fly
                debug = cv2.putText(debug, f"{int(fly.size)}", (int(fly.x), int(fly.y)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 2, cv2.LINE_AA)

    cv2.imshow("Debug Mode", cv2.resize(np.copy(debug), (1280,720)))

    k = cv2.waitKey() & 0xFF

    if k == 27:
        break

    if k == 113:
        CHECKER_MIN_CONTOUR_SIZE = max(0, CHECKER_MIN_CONTOUR_SIZE-KEY_PRESS_MIN_CHANGE_AMOUNT)
    if k == 101:
        CHECKER_MIN_CONTOUR_SIZE = CHECKER_MIN_CONTOUR_SIZE+KEY_PRESS_MIN_CHANGE_AMOUNT
    if k == 97:
        CHECKER_MAX_CONTOUR_SIZE = max(0, CHECKER_MAX_CONTOUR_SIZE-KEY_PRESS_MAX_CHANGE_AMOUNT)
    if k == 100:
        CHECKER_MAX_CONTOUR_SIZE = CHECKER_MAX_CONTOUR_SIZE+KEY_PRESS_MAX_CHANGE_AMOUNT
exit()