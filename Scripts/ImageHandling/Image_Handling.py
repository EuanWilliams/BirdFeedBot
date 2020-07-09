# tensorflow imports
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
import argparse
import sys
import time
import numpy as np
import tensorflow as tf

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

# function to find if image is good
def good_image():
  for filename in os.listdir("/home/pi/BirdFeedBot/BirdFeedBot/ProjectImages"):
      results = str(identify(filename, "GdBd"))
      results_list = results.split(' ')
      prediction = results_list[0]
      accuracy =  ((results_list[1])[7:14])
      if prediction == "Bad" && accuracy > 0.7:
          os.remove(filename)
      elif prediction == "Good" && accuracy > 0.7:
          filepath = ('/home/pi/BirdFeedBot/ProjectImages' + filename)
          newfilepath = ('/home/pi/BirdFeedBot/ProjectImages/ToTweet' + filename)
          os.rename(filepath, newfilepath)
      else:
          archive(filename)

# label images
def label_tweet_image():
  for filename in os.listdir("/home/pi/BirdFeedBot/BirdFeedBot/ProjectImages/ToTweet"):
    results = str(identify(filename, " "))
    results_list = results.split(' ')
    prediction = results_list[0]
    accuracy =  ((results_list[1])[7:14])
    if accuracy <= 0.7:
      archive(filename)
    else:
      text_filename = ("/home/pi/BirdFeedBot/BirdFeedBot/ProjectImages/ToTweet/" + (filename.split("."))[0] ".txt")
      newfile = open(text_filename, "w+")
      newfile.writelines(L) for L = [prediction, accuracy]

# function to archive the files after tweeting
def archive(filename):
  filepath = ('/home/pi/BirdFeedBot/ProjectImages' + filename)
  newfilepath = ('/home/pi/BirdFeedBot/Archive' + filename)
  os.rename(filepath, newfilepath)

good_image()
label_tweet_image()
  
        
