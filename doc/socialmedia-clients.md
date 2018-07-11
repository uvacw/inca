# How to use social media APIs

In this document, we will explain how to connect to social media APIs with INCA, specificially Twitter and YouTube.

## Instantiating Inca
```
from inca import Inca 
myinca = Inca()
```

## Twitter

### Creating an app for Twitter
The app needs to be created once. Just follow the instructions. If no name is used, info will be stored in the default app, and you do not have to specify the appname.
```
myinca.clients.twitter_create_app()
myinca.clients.twitter_create_credentials(appname='YOURAPPNAME')
```

### Collecting Twitter data
Note: When you did not name your app, you do not have to specify the appname. Default will be used instead.
#### By username (timelines)
```
myinca.clients.twitter_timeline(app='YOURAPPNAME', screen_name='SCREENNAME')
```

#### User information
```
myinca.clients.twitter_users_lookup(app='YOURAPPNAME', screen_names=['SNAME1', 'SNAME2', 'SNAME3'])
```
#### Followers
```
myinca.clients.twitter_followers(app='YOURAPPNAME', screen_name='SCREENAME')
```

## YouTube

### Creating an app for YouTube
The process to create a YouTube app is similar to Twitter. Run the command below and follow the instructions. If you decide not to name your app, info will be stored in the default app and you do not have to specicy the appname when creating credentials or collecting data.
```
myinca.clients.youtube_create_app()
myinca.clients.youtube_create_credentials(appname="YOURAPPNAME")
```

### Collecting YouTube data

Note: When you did not name your app, you do not have to specify the appname. Default will be used instead.

#### Videos
The term(s) you want to search for are specified in the `q`, which can take the form of a string or dict. __NOTE: WHAT KIND OF DICT? HOW TO SPECIFY MULTIPLE SEARCH TERMS?__

For other specifications, check out the helpfile with `help(myinca.clients.youtube_videos_search)`
```
myinca.clients.youtube_videos_search(app='YOURAPPNAME', q='SEARCHTERMS')
```

#### Comments on videos and/or channels
Using `parent_id` you can speficy the YouTube ID for which to retrieve comments. You can find the ID in the URL, e.g. for a video: https://<i></i>www.youtube.com/watch?v=__S_VcUXDCXQw__. You can also find this ID in the information you YouTube data you collected using `youtube_videos_search` under 'id'.

Alternatively, you can collect comments on a channel. By using the ID in the URL: https://<i></i>www.youtube.com/channel/__UCdH_8mNJ9vzpHwMNwlz88Zw__, or in the collected YouTube data under 'channelId'.
__NOTE: DOES THIS WORK?__

Other specifications can be found in the helpfile.

```
myinca.clients.youtube_comments(app='YOURAPPNAME', parent_id='VIDEO_OR_CHANNEL_ID')
```

