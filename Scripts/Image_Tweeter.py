# twitter auth
import tweepy
import os
import time

auth = tweepy.OAuthHandler("LSCup96guz1IpLIpRBauC3gK9", "3bFH0pmrT5UNn8Jl7yCi36Xe0LFLqmwOjTpRCvSM6ebgMVVJig")
auth.set_access_token("1270695884280520704-4VtBMNGk6iuFKYFSMuJh0o5JUbzC1R", "JAVfw6VycL8hLnvGb4ZKJHXN7FPBfKjsMNNY9DbnKprkD")
api = tweepy.API(auth)

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

# function to tweet 4 images saved in specific files
def tweet(filename):
    text_filename = ("/home/pi/BirdFeedBot/BirdFeedBot/ProjectImages/ToTweet/" + (filename.split(".j"))[0] +  ".txt")
    label_file = open(text_filename, "r")
    labels = label_file.readlines()
    message = ("Saw a: " + labels[0] + "At: " + (filename.split("."))[0] + "\nAccuracy is: " + labels[1])
    api.update_with_media(("/home/pi/BirdFeedBot/BirdFeedBot/ProjectImages/ToTweet/" + filename), message)
    time.sleep(50000)
    
#function to follow back followers
def follow_back():
    for follower in tweepy.Cursor(api.followers).items():
        follower.follow()

def archive(filename):
    filepath = ('/home/pi/BirdFeedBot/ProjectImages/ToTweet/' + filename)
    newfilepath = ('/home/pi/BirdFeedBot/Archive' + filename)
    os.rename(filepath, newfilepath)


#follow_back()
for filename in os.listdir("/home/pi/BirdFeedBot/BirdFeedBot/ProjectImages/ToTweet"):
    if filename.endswith(".jpg") or filename.endswith(".jpg"):
        tweet(filename)
        continue
    else:
        continue
   
