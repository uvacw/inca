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
The term(s) you want to search for are specified in the `q` parameter. The request can also uses '|', ',' and/or '-'.

- 'term1|term2' matches anything containing either term1 or term2.
- 'term1 -term2' matches anything containing term1 but not term2.
- 'term1,term2' matches anything containing both term1 and term2.

For other parameters, check out the helpfile with `help(myinca.clients.youtube_videos_search)`

```
myinca.clients.youtube_videos_search(app='YOURAPPNAME', q='SEARCHTERMS')
```

#### Comments on videos and/or channels
Using `parent_id` you can specify the YouTube ID for which to retrieve comments. You can find the ID in the URL, e.g. for a video: https://www<span></span>.youtube.com/watch?v=__S_VcUXDCXQw__. You can also find this ID in the information you YouTube data you collected using `youtube_videos_search` under 'id'.

```
myinca.clients.youtube_comments(app='YOURAPPNAME', parent_id='VIDEO_OR_CHANNEL_ID')
```

Alternatively, you can collect comments on a channel. By using the ID in the URL: https://www<span></span>.youtube.com/channel/__UCdH_8mNJ9vzpHwMNwlz88Zw__, or in the collected YouTube data under 'channelId'. When downloading comments from channels, make sure to specify `for_type`. This can be either 'channel' to retrieve comments about the specified channel (i.e. will not include comments left on videos that the channel uploaded) or 'channel+videos' to retrieve all comments associated with the specified channel (i.e. can include comments about the channel or about the channel's videos).

```
myinca.clients.youtube_comments(app='YOURAPPNAME', parent_id='VIDEO_OR_CHANNEL_ID', for_type='channel')
```

Other parameters can be found in the helpfile.

