# USAGE
# # python deep_learning_object_detection.py --image images/example_01.jpg --prototxt MobileNetSSD_deploy.prototxt.txt --model MobileNetSSD_deploy.caffemodel

import numpy as np
import argparse
import cv2
import os
import time
import shutil

count = 0

ap = argparse.ArgumentParser()
ap.add_argument("-i", "--image", help="path to input image")
ap.add_argument("-p", "--prototxt", help="path to Caffe 'deploy' prototxt file")
ap.add_argument("-m", "--model", help="path to Caffe pre-trained model")
ap.add_argument("-c", "--confidence",type=float, default=0.1, help="minimum probability to filter weak detections")
ap.add_argument("-d", "--directory", help="path to target directory")
args = vars(ap.parse_args())

def bird_detect(filename, args):
    CLASSES = ["background", "aeroplane", "bicycle", "bird", "boat", "bottle", "bus", "car", "cat", "chair", "cow",
               "diningtable", "dog", "horse", "motorbike", "person", "pottedplant", "sheep", "sofa", "train",
               "tvmonitor"]
    COLORS = np.random.uniform(0, 255, size=(len(CLASSES), 3))

    net = cv2.dnn.readNetFromCaffe("/home/pi/BirdFeedBot/Scripts/MobileNetSSD_deploy.prototxt.txt", "/home/pi/BirdFeedBot/Scripts/MobileNetSSD_deploy.caffemodel")

    image = cv2.imread(filename)
    (h, w) = image.shape[:2]
    blob = cv2.dnn.blobFromImage(cv2.resize(image, (300, 300)), 0.007843, (300, 300), 127.5)

    net.setInput(blob)
    detections = net.forward()

    items = []

    for i in np.arange(0, detections.shape[2]):
        confidence = detections[0, 0, i, 2]
        if confidence > args["confidence"]:
            idx = int(detections[0, 0, i, 1])
            items.append(CLASSES[idx])

    if "bird" in items:
        print(filename + " Bird", confidence)
        return "bird"
    else:
        print(filename + " No Bird")
        return "nobird"

while 1:
    for filename in os.listdir("/media/pi/My Passport/BirdFeedBot/Unprocessed"):
        filepath = ("/media/pi/My Passport/BirdFeedBot/Unprocessed/" + filename)
        if filename.endswith(".jpg"):
            result = bird_detect(filepath, args)
            if result == "bird":
                count = count + 1
                os.rename(filepath, ('/media/pi/My Passport/BirdFeedBot/OpenCVProcessed/Bird/' + filename))
                print (count)
            if result == "nobird":
                os.rename(filepath, ('/media/pi/My Passport/BirdFeedBot/OpenCVProcessed/No Bird/' + filename))
        else:
            continue
        
    print(count, " Birds found.")
    time.sleep(600)



