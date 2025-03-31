import cv2
import numpy as np
from tkinter.filedialog import askopenfilename

# const 
ARENAS = [

]

# default size
ARENA_SIZE = 100
mouseX = 0
mouseY = 0
IMAGE_RESIZE = (1920,1080)
SELECTED_ARENA = -1


# ask for dialog
imagePath = askopenfilename()

# or uncomment this and comment that to just type a path
# imagePath = ""

# read image into gray
original_image = cv2.imread(imagePath, cv2.IMREAD_COLOR)
original_image = cv2.cvtColor(original_image, cv2.COLOR_RGB2GRAY)
original_image = cv2.cvtColor(original_image, cv2.COLOR_GRAY2RGB)

# resize so it fits on screen
resized_image = cv2.resize(original_image, IMAGE_RESIZE)

# scale the arenas we made to the corerct image size
def transformPointsFromSmallerSize(kps):
    global IMAGE_RESIZE,original_image

    scaleX = original_image.shape[1] / IMAGE_RESIZE[0]
    scaleY = original_image.shape[0] / IMAGE_RESIZE[1]
    newKeyPoints = []

    for kp in kps:
        newKeyPoints.append(cv2.KeyPoint(kp.pt[0] * scaleX, kp.pt[1] * scaleY, kp.size * scaleY))

    return newKeyPoints

# get if mouse is in an arena
def getMouseArenaIndex(x,y):
    for arena in ARENAS:
        radius = arena.size/2
        if np.pow(x - arena.pt[0], 2) + np.pow(y - arena.pt[1], 2) < (radius * radius):
            return ARENAS.index(arena)

    return -1

# draw circles and mouse position
def redrawCircles(image):
    arenas = cv2.drawKeypoints(image, ARENAS, np.array([]), (0,255,0), cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
    
    if SELECTED_ARENA == -1:
        mouse = cv2.circle(arenas, (mouseX, mouseY), ARENA_SIZE, (0,0,255))
        return mouse
    else:
        return arenas
    

# def drawArenasOnOriginalImage():
#     global original_image

#     resizedKps = transformPointsFromSmallerSize(ARENAS)
#     arenas = cv2.drawKeypoints(original_image, resizedKps, np.array([]), (0,255,0), cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
#     return cv2.resize(arenas, IMAGE_RESIZE)

# mouse events!
def mouseEvent(event,x,y,flags,param):
    global mouseX,mouseY,ARENA_SIZE,SELECTED_ARENA

    # if left butto ndown
    if event == cv2.EVENT_LBUTTONDOWN:
        # check if clicking on existing arena
        SELECTED_ARENA = getMouseArenaIndex(x,y)
        if SELECTED_ARENA == -1:
            # if not add a new one at this positiopn
            ARENAS.append(cv2.KeyPoint(x, y, ARENA_SIZE*2))
    # scroll wheel for sizing
    elif event == cv2.EVENT_MOUSEWHEEL:
        if SELECTED_ARENA == -1:
            # if not clicked on arena we just set size for new arena
            ARENA_SIZE += int(np.sign(flags) * 3)
        else:
            if SELECTED_ARENA != -1:
                # ortherwise scale currently selected arena
                ARENAS[SELECTED_ARENA].size += int(np.sign(flags) * 3)
    elif event == cv2.EVENT_LBUTTONUP:
        # unselect on mouse button up
        SELECTED_ARENA = -1
    elif event == cv2.EVENT_RBUTTONDOWN:
        # on right button down over arena delete it
        if SELECTED_ARENA == -1:
            indexOver = getMouseArenaIndex(x,y)
            if indexOver != -1:
                ARENAS.remove(ARENAS[indexOver])
                SELECTED_ARENA = -1
    elif event == cv2.EVENT_MOUSEMOVE:
        # whhen mouse move, if we are selecting an arena we move it!
        if SELECTED_ARENA != -1:
            ARENAS[SELECTED_ARENA].pt = (mouseX, mouseY)

    # updatrer mouse positio
    mouseX,mouseY = x,y

# just to print them out for copying into flyDetector
def printKeyPoints(name, kps):
    print(f"{name} = [")
    for i in range(0, len(kps)):
        kp = kps[i]
        print(f"cv2.KeyPoint({kp.pt[0]}, {kp.pt[1]}, {kp.size}){', ' if i < len(kps)-1 else ''}")
    print("]")

# just to print them out for copying into flyDetector
def saveKeyPoints(kps):
    rescaled = transformPointsFromSmallerSize(kps)

    with open("arenas.txt", "w") as file:
        lines = []
        lines.append("# The unscaled arenas, for use when testing arena creator.")
        lines.append("UNSCALED = [")
        for i in range(0, len(kps)):
            kp = kps[i]
            lines.append(f"cv2.KeyPoint({kp.pt[0]}, {kp.pt[1]}, {kp.size}){', ' if i < len(kps)-1 else ''}")
        lines.append("]")

        lines.append("# The SCALED arenas, for use in fly creator.")
        lines.append("ARENAS = [")
        for i in range(0, len(rescaled)):
            kp = rescaled[i]
            lines.append(f"cv2.KeyPoint({kp.pt[0]}, {kp.pt[1]}, {kp.size}){', ' if i < len(kps)-1 else ''}")
        lines.append("]")

        lines = [f"{line}\n" for line in lines]

        file.writelines(lines)
        file.flush()
        file.close()


# make a window, set mouse call back
cv2.namedWindow('image')
# cv2.namedWindow('resized with arenas')
cv2.setMouseCallback('image',mouseEvent)

# draw cricles
image = redrawCircles(original_image)
cv2.imshow("image", image)
cv2.setWindowProperty('image', cv2.WND_PROP_VISIBLE, 1)
# main loop
while True:
    # show the image
    cv2.imshow("image", image)
    # cv2.imshow('resized with arenas', drawArenasOnOriginalImage())

    # redraw circles
    image = redrawCircles(resized_image)

    # wait for key
    k = cv2.waitKey(20) & 0xFF
    # if escape, close
    if k == 27:
        break
    # if space, spit out arenas!
    elif k == 32:
        printKeyPoints("UNSCALED", ARENAS)
        printKeyPoints("ARENAS", transformPointsFromSmallerSize(ARENAS))


# at end, save arenas to ARENAS.txt
saveKeyPoints(ARENAS)