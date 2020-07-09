import time
from picamera import PiCamera
import RPi.GPIO as GPIO
from datetime import datetime
from time import sleep

camera = PiCamera()

GPIO.setmode(GPIO.BCM)
PIR_PIN = 7
GPIO.setup(PIR_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
camera.rotation = 180
camera.exposure_mode = "sports"
print("SLEEP")
sleep(30)
print("Detecting...")

def MOTION(PIR_PIN):
    print("Motion Detected", str(datetime.today()))
    sleep(0.1)
    for i in range(3):
        camera.capture("/home/pi/BirdFeedBot/TrainingPhotos/" + str(datetime.today()) + ".jpg")

for i in range(400):
    try:
        GPIO.wait_for_edge(PIR_PIN, GPIO.RISING)
        MOTION(PIR_PIN)
    except KeyboardInterrupt:
        print ("Quit")
        GPIO.cleanup()
        camera.close()

GPIO.cleanup()
camera.close()
    
    
