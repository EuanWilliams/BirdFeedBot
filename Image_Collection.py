import time
from picamera import PiCamera
import RPi.GPIO as GPIO
from datetime import datetime
from time import sleep

camera = PiCamera()

GPIO.setmode(GPIO.BCM)
PIR_PIN = 7
GPIO.setup(PIR_PIN, GPIO.IN)
camera.exposure_mode = "sports"
print("Sleep...")
sleep(3)
print("Detecting...")
while 1:
    time_now = datetime.now()
    if (time_now.hour > 4) & (time_now.hour < 10):
        print ("Activating...")
        for i in range(300):
            try:
                GPIO.wait_for_edge(PIR_PIN, GPIO.RISING)
                for i in range(4):
                    camera.capture("/media/pi/My Passport/BirdFeedBot/Unprocessed/" + str(datetime.today()) + ".jpg")
                print("Motion Detected", str(datetime.today()))
            except KeyboardInterrupt:
                print ("Quit")
                GPIO.cleanup()
                camera.close()
    else:
        print("Sleeping until 4am...")
        time.sleep(3600)
GPIO.cleanup()
camera.close()
    
    
