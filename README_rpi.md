# README.md
Setting up RPi to read button press from GPIO, set LED, take picture, perform
averaging

make sure to enable picam in raspi-config (i think?)

output directory is `/capstone/pictures` (make sure this exists and has 777
permissions)

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
python-rpi.gpio
python3-rpi.gpio
cv2
numpy
picamera
```