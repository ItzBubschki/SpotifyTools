If you want to use one of the scripts you have to create a new spotify application from the dashboard. <br>
Afterwards you have to create a new file called `.env` where you have to paste the following:

```
SPOTIPY_CLIENT_ID=<your client id>
SPOTIPY_CLIENT_SECRET=<your client secret>
SPOTIPY_REDIRECT_URI=<your redirect url>
EMAIL_PASSWORD=<your smtp password>
EMAIL_SENDER=<your email account>
SMTP_HOST=<smtp host>
SMTP_PORT=<smtp port>
```

If you want to use the playlist adder you have to use ngrok to point to a random port on your system and add the ngrok url on the spotify dashboard to your allowed redirect urls.