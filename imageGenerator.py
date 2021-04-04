import spotipy
import urllib.request
import smtplib
import os

from spotipy.oauth2 import SpotifyClientCredentials
from PIL import Image
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from dotenv import load_dotenv

load_dotenv()

sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials())

url = input("enter spotify url: ")

try:
    if (url.__contains__("episode")):
        response = sp.episode(url, market="DE")
        image_url = response['images'][0]['url']
    else:
        response = sp.track(url)
        image_url = response['album']['images'][0]['url']
except Exception:       
    print("please enter a valid spotify id")
    quit()

song_name = response['name']
urllib.request.urlretrieve(image_url, "thumbnail.jpg")
image = Image.open("thumbnail.jpg")
background = Image.new('RGB', (900, 2000), 'black')
image_copy = background.copy()
position_x = background.width/2 - image.width/2
position_y = background.height/2 - image.height/2
position = (int(position_x), int(position_y))
image_copy.paste(image, position)
image_copy.save("resized.jpg")

reciever = input("Enter your mail adress: ")
if len(reciever) > 0:
    s = smtplib.SMTP(host=os.environ['SMTP_HOST'], port=os.environ['SMTP_PORT'])
    s.starttls()
    s.login(os.environ['EMAIL_SENDER'], os.environ['EMAIL_PASSWORD'])
    msg = MIMEMultipart()
    msg['From'] = os.environ['EMAIL_SENDER']
    msg['To'] = reciever
    msg['Subject'] = f"thumbnail-{song_name}"
    img_data = open("resized.jpg", 'rb').read()
    img = MIMEImage(img_data, name=os.path.basename("resized.jpg"))
    msg.attach(img)
    s.send_message(msg)
    s.quit()