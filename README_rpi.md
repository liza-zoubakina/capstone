# README.md
Setting up RPi to read button press from GPIO, set LED, take picture, perform
averaging

make sure to enable picam in raspi-config (i think?)

output directory is `/capstone/pictures/` (make sure this exists and has 777
permissions)

picture log is `/capstone/pictures_log/`
New images are saved as `date-time-before.jpg` and `date-time-after.jpg`

output log is `/capstone/pixel_averages.log`
`date time before_pixel_average after_pixel_average after-before`

## Initial setup
`sudo apt upgrade all`
install the packages below

## links
see these links for connections:
### LED
[LED](https://thepihut.com/blogs/raspberry-pi-tutorials/27968772-turning-on-an-led-with-your-raspberry-pis-gpio-pins)

### buttons
[buttons](https://raspberrypihq.com/use-a-push-button-with-raspberry-pi-gpio/)

### camera
[camera](https://projects.raspberrypi.org/en/projects/getting-started-with-picamera/0)

## packages

`{sudo apt install} `
```
python
python-rpi.gpio
python3-rpi.gpio
cv2
numpy
picamera
```
