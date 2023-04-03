import os
from picamera2 import Picamera2, Preview
import time
import RPi.GPIO as GPIO
from gpiozero import Button
from signal import pause
import datetime
import cv2 
import numpy as np
	
# define parameters
SF = .2 # image scaling. make smaller for faster
PICTURE_PATH = '/capstone/pictures' # path where pictures are saved. Every time state == 0, this is overwritten
THRESHOLD = .02 # to be tuned
SLEEP_TIME = 2 # amount of time for camera to 'warm up'. Sample code has 5, but suggests min of 2 seconds

LOG_FILE = '/capstone/pixel_averages.log'
LOG_PICTURES = '/capstone/pictures_log'

# define RPi pinout
BUTTON = 10
BEFORE = 11
AFTER = 12
DISPLAY = 13
QUIT = 15
	
# Set up camera
picam2 = Picamera2()

#picam2.start_and_capture_file("test2.jpg")
camera_config = picam2.create_still_configuration(main={"size": (1920,1080)},
						lores = {"size":(640, 480)},
						display="lores")
picam2.configure(camera_config)

def time_to_string():
    time_now = datetime.datetime.now()
    ret = time_now.strftime("%y-%m-%d_%H-%M-%S") # formats as YY-MM-DD_HH-MM-SS
    return ret

def pic_capture(channel):
	print("made it here")
	picam2.start_preview(Preview.QT)
	timestamp = time_to_string()
	picam2.start()
	time.sleep(5)
	picam2.capture_file('pictures/%s.jpg' % timestamp)
	picam2.stop_preview()
	picam2.stop()

# Set up RPi GPIO
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)

GPIO.setup(BUTTON,GPIO.IN, pull_up_down=GPIO.PUD_DOWN) #next step button {before, after, print results}
GPIO.add_event_detect(BUTTON, GPIO.RISING, callback=pic_capture, bouncetime = 500)



message = input("Press enter to quit\n\n")
GPIO.cleanup()


'''
print("taking picture")
os.system("libcamera-jpeg -o ~/capstone/test.jpg -n")
print("done taking picture")
'''


