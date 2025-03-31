import time, datetime
from picamera2 import Picamera2, Preview

picam = Picamera2()

def check_exposure(dt: datetime.datetime):
    # 8 am bc anything AFTER 7, after 8pm off because anything LESS than 8
    if dt.hour > 8 and dt.hour < 21:
    #if dt.minute == 38:# this can be uncommented and line above commented out for testing, if its like that minute it'll do the first one
        return 1500
    else:
        return 4500
#usually 750 day 1600 night
capture_config = picam.create_still_configuration({"size": (1920, 1080)})
picam.configure(capture_config)

exposure = check_exposure(datetime.datetime.now())

#picam.set_controls({"AwbEnable":False, "AeEnable": False, "ExposureTime": exposure, "AnalogueGain": 0.0})

preview_config = picam.create_preview_configuration()


picam.start(show_preview=True)

picam.switch_mode(preview_config)

for i in range(1,7200): #take number of photos (last-first)
    # added date time tracking
    dt = datetime.datetime.now()
    
    # check new exposure for time
    new_exp = check_exposure(dt)
    # only actually change it on the camera if it changes
    if new_exp != exposure:
        exposure = new_exp
        picam.stop() 
        picam.configure(capture_config)
        #picam.set_controls({"ExposureTime": exposure})
        picam.start(show_preview=True)

    # format date to MM-DD-YYYY-HHMMss
    format_datetime = time.strftime("%m-%d-%Y-%H%M%S")
    # files now image-MM-DD-YYYY-HHMMss-XXXX
    # pad the i variable so its always 4 long, makes matlab side easier
    picam.switch_mode_and_capture_file(capture_config, f"image-{format_datetime}-{i:04}.png")
    print(f"Captured image {i}")
    picam.switch_mode(preview_config)
    time.sleep(1) #time between photos
    
picam.stop()
