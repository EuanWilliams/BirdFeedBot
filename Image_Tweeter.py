# twitter auth
import tweepy
import os
import time
from datetime import datetime

auth = tweepy.OAuthHandler("LSCup96guz1IpLIpRBauC3gK9", "3bFH0pmrT5UNn8Jl7yCi36Xe0LFLqmwOjTpRCvSM6ebgMVVJig")
auth.set_access_token("1270695884280520704-4VtBMNGk6iuFKYFSMuJh0o5JUbzC1R", "JAVfw6VycL8hLnvGb4ZKJHXN7FPBfKjsMNNY9DbnKprkD")
api = tweepy.API(auth)

# function to ask @euan_williams1 account what to do with images
def direct_message(filename):
    filepath = ('/media/pi/My Passport/BirdFeedBot/OpenCVProcessed/Bird/' + filename)
    res = api.media_upload("/media/pi/My Passport/BirdFeedBot/OpenCVProcessed/Bird/" + filename)
    api.send_direct_message("2883155739", text = "Would you like me to tweet this?", attachment_type = "media", attachment_media_id = res.media_id)
    while True:
        time.sleep(120)
        dm_list = api.list_direct_messages(1)
        message_dict = getattr(dm_list[0], 'message_create')
        last_dm = (message_dict['message_data']['text'])
        print (last_dm)
        if last_dm == "Yes":
            api.send_direct_message("2883155739", text = "Tweeted.")
            tweet(filename)
            newfilepath = ('/media/pi/My Passport/BirdFeedBot/Archive/Tweeted/' + filename)
            os.rename(filepath, newfilepath)
            time.sleep(3600)
            break
        elif last_dm == "No":
            api.send_direct_message("2883155739", text = "Not Tweeted.")
            newfilepath = ('/media/pi/My Passport/BirdFeedBot/Archive/Not Tweeted/' + filename)
            os.rename(filepath, newfilepath)
            break
        elif last_dm == "Sleep":
            api.send_direct_message("2883155739", text = "Sleeping.")
            time.sleep(1800)
        else:
            time.sleep(240)
            continue

# function to tweet 4 images saved in specific files
def tweet(filename):
    #text_filename = ("/home/pi/BirdFeedBot/BirdFeedBot/ProjectImages/ToTweet/" + (filename.split(".j"))[0] +  ".txt")
    #label_file = open(text_filename, "r")
    #labels = label_file.readlines()
    #message = ("Saw a: " + labels[0] + "At: " +  + "\nAccuracy is: " + labels[1])
    message = ("Taken at: " + (filename.split("."))[0])
    filepath = ("/media/pi/My Passport/BirdFeedBot/OpenCVProcessed/Bird/" + filename)
    api.update_with_media(filepath, message)
    
#function to follow back followers
def follow_back():
    for follower in tweepy.Cursor(api.followers).items():
        follower.follow()
 

while 1:
   # follow_back()
    for filename in os.listdir("/media/pi/My Passport/BirdFeedBot/OpenCVProcessed/Bird"):
        now = (datetime.today())
        if now.hour >= 20:
            print("Sleeping until 11am...")
            time.sleep(50400)
        else:
            if filename.endswith(".jpg") or filename.endswith(".jpg"):
                direct_message(filename)
                continue
            else:
                continue

    time.sleep(300)
   
