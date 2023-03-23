import RPi.GPIO as GPIO
from picamera import PiCamera
from time import sleep
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

# Set up RPi GPIO
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)

GPIO.setup(BUTTON,GPIO.IN, pull_up_down=GPIO.PUD_DOWN) #next step button {before, after, print results}
GPIO.add_event_detect(BUTTON, GPIO.RISING, callback=button_callback, bouncetime=200)

GPIO.setup(QUIT,GPIO.IN, pull_up_down=GPIO.PUD_DOWN) #quit button
GPIO.add_event_detect(BUTTON, GPIO.RISING, callback=cleanup, bouncetime=200)

GPIO.setup(BEFORE,GPIO.OUT) #idle/ready for before picture indicator LED
GPIO.setup(AFTER,GPIO.OUT) #ready for after picture indicator LED
GPIO.setup(DISPLAY,GPIO.OUT) #ready to display result indicator LED

camera = PiCamera()
#camera.rotation = {0, 90, 180, 270) # use if image is rotated

# Set up log file
file = open(LOG_FILE, 'a')

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
button_flag = 0
print_once = 1
current_time = time_to_string()

#button callback functions
def button_callback(channel):
    # Call back function for button press in it's own thread.
    # Think of this as an interrupt
    if state == 0 or state == 2 or state == 5: # only set flag if in correct state
        button_flag = 1
    return

def cleanup(channel):
    #cleanup before quitting
    GPIO.cleanup()
    file.close()
    exit()
    return

#CV functions
def get_pixel_average(picture_path): 
    # takes image path, removes background, finds average pixel value in foreground
    img = cv2.imread('pla_1.jpg')
    img = cv2.blur(img,(25,25))

    w = int(SF*img.shape[1])
    h = int(SF*img.shape[0])
    img = cv2.resize(img,(w,h))

    imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

# Otsu's thresholding
    _, threshold_mask = cv2.threshold(imgGray,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)

    mask_threshold = np.zeros_like(img)
    mask_threshold[:, :, 0] = threshold_mask # set channel 0 to the mask
    mask_threshold[:, :, 1] = threshold_mask # ditto for channel 1
    mask_threshold[:, :, 2] = threshold_mask # ditto for channel 2

    mask_threshold = cv2.bitwise_not(mask_threshold);
    masked_eddie = cv2.bitwise_and(img, mask_threshold)
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
    file.write(time + ' ' + before + ' ' + after + ' ' + diff + '\n')
    return



# main loop
while True:
    if state == 0: #idle
        GPIO.output(BEFORE, GPIO.HIGH) #show idle LED
        if print_once:
            print("Ready for before picture. Insert sample.")
            print_once = 0
        if button_flag: #button pressed
            print("Button pressed, taking before picture, wait until prompted before removing sample")
            current_time = time_to_string() # get date and time for log 
            GPIO.output(BEFORE, GPIO.LOW) #no longer idle
            state = 1
    else if state == 1: #take picture before
        camera.start_preview()
        sleep(SLEEP_TIME)
        camera.capture(PICTURE_PATH + '/before.jpg')
        camera.stop_preview()
        print_once = 1
        state == 2
    else if state == 2: #wait for acetoning by hooman
        GPIO.output(AFTER, GPIO.HIGH) #show waiting for sample LED
        if print_once:
            print("Ready for after picture. Remove sample, apply acetone, allow to dry, place sample, push button.")
            print_once = 0
        if button_flag: #button pressed
            print("Button pressed, taking after picture, wait until prompted before removing sample")
            GPIO.output(AFTER, GPIO.LOW) #no longer waiting
            state == 3
    else if state == 3: #take picture after
        camera.start_preview()
        sleep(SLEEP_TIME)
        camera.capture(PICTURE_PATH + '/after.jpg')
        camera.stop_preview()
        print_once = 1
        state == 4
    else if state == 4: #calculate values
        print("calculating before pixel average")
        before_average = get_pixel_average(PICTURE_PATH + '/before.jpg')
        print("calculating after pixel average")
        after_average = get_pixel_average(PICTURE_PATH + '/after.jpg')
        diff = after_average-before_average
        state == 5
    else if state == 5: #values ready to display
        GPIO.output(DISPLAY, GPIO.HIGH) #show ready to display values LED
        if print_once:
            print("Press button to display results. ")
            print_once = 0
        if button_flag: #button pressed
            print("Button pressed, displaying results")
            GPIO.output(AFTER, GPIO.LOW) #no longer ready
            state == 6
    else if state == 6: #display values, determine if petg or pla
        print("Before: " + before_average)
        print("After:  " + after_average)
        print("Difference: " + diff)
        if diff > THRESHOLD:
            print("This part is PLA")
        else:
            print("This part is PETG")
        print_once = 1
        copy_pictures_to_log(time)
        write_log(time, before_average, after_average, diff)
        state = 0 #restart loop for next sample
