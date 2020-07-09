# tensorflow imports
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
import argparse
import sys
import time
import numpy as np
import tensorflow as tf

# general imports
from time import sleep
from datetime import datetime
import os
import glob
import shutil
import time

# twitter auth
import tweepy
auth = tweepy.OAuthHandler("LSCup96guz1IpLIpRBauC3gK9", "3bFH0pmrT5UNn8Jl7yCi36Xe0LFLqmwOjTpRCvSM6ebgMVVJig")
auth.set_access_token("1270695884280520704-4VtBMNGk6iuFKYFSMuJh0o5JUbzC1R", "JAVfw6VycL8hLnvGb4ZKJHXN7FPBfKjsMNNY9DbnKprkD")
api = tweepy.API(auth)

# camera settings
from picamera import PiCamera
camera = PiCamera()
camera.rotation = 180
camera.shutter_speed = 6000

# motion sensor settings
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
PIR_PIN = 7
GPIO.setup(PIR_PIN, GPIO.IN)

# load graph function for tensorflow
def load_graph(model_file):
  graph = tf.Graph()
  graph_def = tf.GraphDef()

  with open(model_file, "rb") as f:
    graph_def.ParseFromString(f.read())
  with graph.as_default():
    tf.import_graph_def(graph_def)

  return graph


# read tensors function for tensorflow
def read_tensor_from_image_file(file_name, input_height=299, input_width=299,
				input_mean=0, input_std=255):
  input_name = "file_reader"
  output_name = "normalized"
  file_reader = tf.read_file(file_name, input_name)
  if file_name.endswith(".png"):
    image_reader = tf.image.decode_png(file_reader, channels = 3,
                                       name='png_reader')
  elif file_name.endswith(".gif"):
    image_reader = tf.squeeze(tf.image.decode_gif(file_reader,
                                                  name='gif_reader'))
  elif file_name.endswith(".bmp"):
    image_reader = tf.image.decode_bmp(file_reader, name='bmp_reader')
  else:
    image_reader = tf.image.decode_jpeg(file_reader, channels = 3,
                                        name='jpeg_reader')
  float_caster = tf.cast(image_reader, tf.float32)
  dims_expander = tf.expand_dims(float_caster, 0);
  resized = tf.image.resize_bilinear(dims_expander, [input_height, input_width])
  normalized = tf.divide(tf.subtract(resized, [input_mean]), [input_std])
  sess = tf.Session()
  result = sess.run(normalized)

  return result


# load labels function for tensorflow
def load_labels(label_file):
  label = []
  proto_as_ascii_lines = tf.gfile.GFile(label_file).readlines()
  for l in proto_as_ascii_lines:
    label.append(l.rstrip())
  return label


# tensorflow image classification
def identify(filename, classification_type):
    if classification_type == "GdBd":
        file_name = ("/home/pi/Desktop/tensorflow_testing/tensorflow-for-poets-2/tf_files/flower_photos/daisy/" + filename + ".jpg")
        model_file = "/home/pi/Desktop/tensorflow_testing/tensorflow-for-poets-2/tf_files/retrained_graph.pb"
        label_file = "/home/pi/Desktop/tensorflow_testing/tensorflow-for-poets-2/tf_files/retrained_labels.txt"
    else:
        file_name = ("/home/pi/Desktop/tensorflow_testing/tensorflow-for-poets-2/tf_files/flower_photos/daisy/" + filename + ".jpg")
        model_file = "/home/pi/Desktop/tensorflow_testing/tensorflow-for-poets-2/tf_files/retrained_graph.pb"
        label_file = "/home/pi/Desktop/tensorflow_testing/tensorflow-for-poets-2/tf_files/retrained_labels.txt"
        
    input_height = 224
    input_width = 224
    input_mean = 128
    input_std = 128
    input_layer = "input"
    output_layer = "final_result"

    graph = load_graph(model_file)
    t = read_tensor_from_image_file(file_name,
                                    input_height=input_height,
                                    input_width=input_width,
                                    input_mean=input_mean,
                                    input_std=input_std)

    input_name = "import/" + input_layer
    output_name = "import/" + output_layer
    input_operation = graph.get_operation_by_name(input_name);
    output_operation = graph.get_operation_by_name(output_name);

    with tf.Session(graph=graph) as sess:
      start = time.time()
      results = sess.run(output_operation.outputs[0],
                        {input_operation.outputs[0]: t})
      end=time.time()
    results = np.squeeze(results)

    top_k = results.argsort()[-5:][::-1]
    labels = load_labels(label_file)

    template = "{} (score={:0.5f})"
    for i in top_k:
      return template.format(labels[i], results[i])


# function to tweet 4 images saved in specific files
def tweet(message):
    filenames = ['/home/pi/BirdFeedBot/ProjectImages/image0.jpg', '/home/pi/BirdFeedBot/ProjectImages/image1.jpg', '/home/pi/BirdFeedBot/ProjectImages/image2.jpg', '/home/pi/BirdFeedBot/ProjectImages/image3.jpg']
    media_ids = []
    for filename in filenames:
        res = api.media_upload(filename)
        media_ids.append(res.media_id)
    api.update_status(status=message, media_ids=media_ids)

# function to take 4 images and save to a specific file name, then call the direct message function
def take_photo():
    for i in range(4):
        camera.capture('/home/pi/BirdFeedBot/ProjectImages/image%s.jpg' % i)
    direct_message()
        
# function to archive the files after tweeting
def archive():
    for i in range(4):
        today = str(datetime.today())
        filepath = ('/home/pi/BirdFeedBot/ProjectImages/image'+ str(i) +'.jpg')
        newfilepath = ('/home/pi/BirdFeedBot/Archive/'+ today +'.jpg')
        os.rename(filepath, newfilepath)

# function to ask @euan_williams1 account what to do with images
def direct_message():
    filenames = ['/home/pi/BirdFeedBot/ProjectImages/image0.jpg', '/home/pi/BirdFeedBot/ProjectImages/image1.jpg', '/home/pi/BirdFeedBot/ProjectImages/image2.jpg', '/home/pi/BirdFeedBot/ProjectImages/image3.jpg']
    api.send_direct_message("2883155739", text = "Would you like me to tweet this?")
    for filename in filenames:
        res = api.media_upload(filename)
        api.send_direct_message("2883155739", attachment_type = "media", attachment_media_id = res.media_id)
    while True:
        sleep(240)
        dm_list = api.list_direct_messages(1)
        message_dict = getattr(dm_list[0], 'message_create')
        last_dm = (message_dict['message_data']['text'])
        print (last_dm)
        if last_dm == "Yes":
            api.send_direct_message("2883155739", text = "Tweeted.")
            time = str(datetime.today())
            print (time)
            tweet(time)
            archive()
            break
        elif last_dm == "No":
            api.send_direct_message("2883155739", text = "Not Tweeted.")
            archive()
            break
        else:
            continue

    sleep(1800)
    main()
    
#function to follow back followers
def follow_back():
    for follower in tweepy.Cursor(api.followers).items():
        follower.follow()
    
    
# function to detect motion and begin handling.
def motion_detection():
    try:
        GPIO.add_event_detect(PIR_PIN, GPIO.RISING, callback=take_photo)
        while 1:
            time.sleep(100)
    except KeyboardInterrupt:
        GPIO.cleanup()    

def main():
    follow_back()
    now = datetime.now()
    current_time = now.strftime("%H")
    while True:
        if current_time >= 22 or current_time < 9:
            sleep(39600)
            main()
        else:
            motion_detection()

    
filename = input(str("Please input the filename: "))
results = str(identify(filename, "ree"))
results_list = results.split(' ')
prediction = results_list[0]
accuracy =  ((results_list[1])[7:14])
print(prediction)
print(accuracy)







































    

