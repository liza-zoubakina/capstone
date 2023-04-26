import board
import datetime
import neopixel
import RPi.GPIO as GPIO
import shutil
from time import sleep

from picamera2 import Picamera2 as PiCamera
from picamera2 import Preview

import cv2 
import numpy as np

# define parameters
SF = .8 # image scaling. make smaller for faster
PICTURE_PATH = '/home/pi/capstone/pictures' # path where pictures are saved. Every time state == 0, this is overwritten
THRESHOLD = .02 # to be tuned
SLEEP_TIME = 2 # amount of time for camera to 'warm up'. Sample code has 5, but suggests min of 2 seconds
CROP_FACTOR = 1

LOG_FILE = '/home/pi/capstone/pixel_averages.log'
LOG_PICTURES = '/home/pi/capstone/pictures_log'

# define RPi pinout
BUTTON = board.D15.id #board.D15 #board pin 10
# BEFORE = 11
# AFTER = 12
# DISPLAY = 13
# QUIT = 15

# neopixel setup code
NEOPIXEL = board.D18 #board pin 12
num_pixels = 24
ORDER = neopixel.GRB

pixels = neopixel.NeoPixel(NEOPIXEL, num_pixels, brightness=0.2, auto_write = False, pixel_order = ORDER)




#################################
'''
states:
    0: idle
    1: button pressed, going to take before picture
    2: before picture taken, waiting for next button press
    3: button pressed, going to take after picture
    4: after picture taken, calculating results
    5: calculating results, waiting for button press
    6: button pressed, printing results
'''

#global vars
state = 0
print_once = 1
button_flag = 0

#button callback functions
def button_callback(channel):
    global button_flag
    # Call back function for button press in it's own thread.
    # Think of this as an interrupt
    if state == 0 or state == 2 or state == 5: # only set flag if in correct state
        button_flag = 1
    return

def cleanup(channel):
    #cleanup before quitting
    GPIO.cleanup()
    exit()
    return

#CV functions
def get_pixel_average(picture_path, string):
    # takes image path, removes background, finds average pixel value in foreground
    img = cv2.imread(picture_path)
    # img = cv2.blur(img,(25,25))
    img = cv2.blur(img,(5,5))

    w = int(img.shape[1])
    h = int(img.shape[0])

    
    # img = cv2.resize(img,(int(SF*w),int(SF*h)))
    # img = img[int(h/CROP_FACTOR*2):int(h/CROP_FACTOR*3), int(w/CROP_FACTOR*2):int(w/CROP_FACTOR*3)] # crop to only middle fifth of picture
    img = img[int(h/4):int(h/4*3), int(w/3):int(w/3*2)] # crop to only middle fifth of picture

    imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

# Otsu's thresholding
    _, threshold_mask = cv2.threshold(imgGray,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)

    mask_threshold = np.zeros_like(img)
    mask_threshold[:, :, 0] = threshold_mask # set channel 0 to the mask
    mask_threshold[:, :, 1] = threshold_mask # ditto for channel 1
    mask_threshold[:, :, 2] = threshold_mask # ditto for channel 2

    mask_threshold = cv2.bitwise_not(mask_threshold);
    masked_eddie = cv2.bitwise_and(img, mask_threshold)
    # cv2.imwrite(PICTURE_PATH + "/nomask.jpg", mask_threshold)
    cv2.imwrite(PICTURE_PATH + "/maskededdie_" + string + ".jpg", masked_eddie)
    cv2.imwrite(PICTURE_PATH + "/nomask.jpg_" + string + ".jpg", img)

    return calculate_average(img, mask_threshold)

def calculate_average(img, mask):
    # iterates through img, multiplies by mask, averages pixel value
    dimensions = img.shape; # [height, width, channels]
    pixel_average = 0 #average value of not background pixels
    pixel_count = 0 # number of pixels which aren't background
    for i in range (dimensions[0]):
        for j in range (dimensions[1]):
            pixel_sum = 0 # average value of one pixel
            for k in range (dimensions[2]):
                pixel_sum += img[i][j][k]
            pixel_sum /= dimensions[2] # divide by number of channels
            if mask[i][j][0]: # if mask at this pixel is 1
                pixel_average += pixel_sum # add to average value of all pixels
                pixel_count += mask[i][j][0] # add to pixel counter
    pixel_average /= pixel_count
    return pixel_average


# other helpers
def time_to_string():
    time_now = datetime.datetime.now()
    ret = time_now.strftime("%y-%m-%d_%H-%M-%S") # formats as YY-MM-DD_HH-MM-SS
    return ret

def copy_pictures_to_log(time):
    shutil.copyfile(PICTURE_PATH + '/before.jpg', LOG_PICTURES + '/' + time + '_before.jpg')
    shutil.copyfile(PICTURE_PATH + '/after.jpg', LOG_PICTURES + '/' + time + '_after.jpg')
    return

def write_log(time, before, after, diff):
    file = open(LOG_FILE, 'a')
    file.write(str(time) + ' ' + str(before) + ' ' + str(after) + ' ' + str(diff) + '\n')
    file.close()
    return

def neopixel_on():
    pixels.fill((255, 255, 255))
    pixels.show()
    return
def neopixel_off():
    pixels.fill((0, 0, 0))
    pixels.show()
    return

# print(GPIO.getmode())

# Set up RPi GPIO
GPIO.setwarnings(False)
# GPIO.setmode(GPIO.BOARD)

GPIO.setup(BUTTON,GPIO.IN, pull_up_down=GPIO.PUD_DOWN) #next step button {before, after, print results}
GPIO.add_event_detect(BUTTON, GPIO.RISING, callback=button_callback, bouncetime=1000)

# GPIO.setup(QUIT,GPIO.IN, pull_up_down=GPIO.PUD_DOWN) #quit button
# GPIO.add_event_detect(QUIT, GPIO.RISING, callback=cleanup, bouncetime=200)

# GPIO.setup(BEFORE,GPIO.OUT) #idle/ready for before picture indicator LED
# GPIO.setup(AFTER,GPIO.OUT) #ready for after picture indicator LED
# GPIO.setup(DISPLAY,GPIO.OUT) #ready to display result indicator LED

camera = PiCamera()
PiCamera.set_logging(PiCamera.DEBUG)
#camera.rotation = {0, 90, 180, 270) # use if image is rotated
camera_config = camera.create_still_configuration(
        main = {"size": (1920, 1080)},
        lores = {"size": (640, 480)},
        display = "lores")
camera.configure(camera_config)

current_time = time_to_string()

# main loop
while True:
    # print(button_flag)
    if state == 0: #idle
        # GPIO.output(BEFORE, GPIO.HIGH) #show idle LED
        if print_once:
            print("Ready for before picture. Insert sample. Press enter to continue")
            print_once = 0
        # if button_flag: #button pressed
        if input()=='': #button pressed
            print("Button pressed, taking before picture, wait until prompted before removing sample")
            current_time = time_to_string() # get date and time for log 
            # GPIO.output(BEFORE, GPIO.LOW) #no longer idle
            state = 1
            # button_flag = 0
    elif state == 1: #take picture before
        neopixel_on()
        camera.start_preview(Preview.QT)
        camera.start()
        sleep(SLEEP_TIME)
        camera.capture_file(PICTURE_PATH + '/before.jpg')
        camera.stop_preview()
        camera.stop()
        neopixel_off()
        print_once = 1
        state = 2
    elif state == 2: #wait for acetoning by hooman
        # GPIO.output(AFTER, GPIO.HIGH) #show waiting for sample LED
        if print_once:
            print("Ready for after picture. Remove sample, apply acetone, allow to dry, place sample, push button.")
            print_once = 0
        # if button_flag: #button pressed
        if input()=='': #button pressed
            print("Button pressed, taking after picture, wait until prompted before removing sample")
            # GPIO.output(AFTER, GPIO.LOW) #no longer waiting
            state = 3
            # button_flag = 0
    elif state == 3: #take picture after
        neopixel_on()
        camera.start_preview(Preview.QT)
        camera.start()
        sleep(SLEEP_TIME)
        camera.capture_file(PICTURE_PATH + '/after.jpg')
        camera.stop_preview()
        camera.stop()
        neopixel_off()
        print_once = 1
        state = 4
    elif state == 4: #calculate values
        print("calculating before pixel average")
        before_average = get_pixel_average(PICTURE_PATH + '/before.jpg', 'before')
        print("calculating after pixel average")
        after_average = get_pixel_average(PICTURE_PATH + '/after.jpg', 'after')
        diff = after_average-before_average
        state = 5
    elif state == 5: #values ready to display
        # GPIO.output(DISPLAY, GPIO.HIGH) #show ready to display values LED
        if print_once:
            print("Press button to display results. ")
            print_once = 0
        # if button_flag: #button pressed
        if input()=='': #button pressed
            print("Button pressed, displaying results")
            # GPIO.output(DISPLAY, GPIO.LOW) #no longer ready
            state = 6
    elif state == 6: #display values, determine if petg or pla
        print("Before: " + str(before_average))
        print("After:  " + str(after_average))
        print("Difference: " + str(diff))
        if diff > THRESHOLD:
            print("This part is PLA")
        else:
            print("This part is PETG")
        print_once = 1
        copy_pictures_to_log(current_time)
        write_log(current_time, before_average, after_average, diff)
        print("Wrote to log file")
        print("\n=================================\n")
        state = 0 #restart loop for next sample
