from picamera2 import Picamera2 as PiCamera
from picamera2 import Preview
camera = PiCamera()
camera_config = camera.create_still_configuration(
        main = {"size": (1920, 1080)},
        lores = {"size": (640, 480)},
        display = "lores")
camera.configure(camera_config)
camera.start_preview(Preview.QT)
camera.start()
input()
camera.stop_preview()
camera.stop()
