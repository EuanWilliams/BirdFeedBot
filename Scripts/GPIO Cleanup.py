import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
PIR_PIN = 14
GPIO.setup(PIR_PIN, GPIO.IN)

GPIO.cleanup()
