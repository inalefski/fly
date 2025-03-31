import cv2

## Folder where the program looks for images
IMAGE_FOLDER = "images"
## Allowed file extensions 
ALLOWED_EXTENSIONS = ("png", "jpg", "PNG")
## Maxing out the colour on the background and image, 0 is black, 255 is white
COLOR_MAX = (245,245,245)
BLUR_RADIUS = (0,0)
USE_BLUR= False
USE_COLOR_MAX= False
## Image to get background
BACKGROUND_IMAGE = "background1.png"
## What colour does it binarize at? usually 7 or 8 for ir, 15 or 14 for visible
IMAGE_THRESHOLD = 25
## Min/Max Conotur sizes, might not be needed
MIN_CONTOUR_SIZE = 125
MAX_CONTOUR_SIZE = 2500

## How many flies per arena
EXPECTED_FLY_COUNT = 10
EXPECTED_FLY_AREA = 175

## How many pixels can a fly move to be staying still?
FLY_MATCH_CI = 1
FLY_MATCH_SIZE_CI = 1

## Image resizing (slides are 1280,720 and regular images are 1440,1080) or 1920,1080
IMAGE_RESIZE_TO = (1920,1080) 
IMAGE_RESIZE_ENABLE = False

## Contour movement check
CONTOUR_MATCH_CI = 2
CONTOUR_MISMATCH_ALLOWANCE = 1
CONTOUR_POINT_MISMATCH_ALLOWANCE = 1

## Save image mode
SAVE_DEBUG_IMAGES = True
DEBUG_IMAGE_COUNT = 500000
DEBUG_IMAGE_OUTPUT_DIR = "./output_images"

## Test mode to check setup
ENABLE_TEST_MODE = False
## Minimum 1 as it takes this one and the one before it
TEST_IMAGE_ID = 2500
TEST_IMAGE_SIZE=(1280,720)

## Arenas
ARENAS = [
cv2.KeyPoint(495.0, 145.0, 236.0), 
cv2.KeyPoint(794.0, 130.0, 236.0), 
cv2.KeyPoint(500.0, 410.0, 236.0), 
cv2.KeyPoint(801.0, 398.0, 242.0), 
cv2.KeyPoint(514.0, 678.0, 242.0), 
cv2.KeyPoint(812.0, 667.0, 242.0), 
cv2.KeyPoint(1293.0, 126.0, 236.0), 
cv2.KeyPoint(1576.0, 130.0, 230.0), 
cv2.KeyPoint(1304.0, 389.0, 236.0), 
cv2.KeyPoint(1585.0, 388.0, 236.0), 
cv2.KeyPoint(1311.0, 653.0, 236.0), 
cv2.KeyPoint(1592.0, 642.0, 236.0)
]



## Output settings
DATA_OUTPUT_DIR = "./data"
DATA_EXPORT_JSON = True
DATA_EXPORT_CSV = True