# How to use social media APIs

This is a first draft for a tutorial on how to connect to social media APIs with INCA.



## Instantiating Inca
```
from inca import
Inca inca = Inca()
```

## Creating an app for Twitter
App needs to be created once. If no name used, info will be stored in the default app.
```
inca.clients.twittercreateapp()
inca.clients.twittercreatecredentials()
```

## Collecting Twitter data

### By username (timelines)
```
inca.clients.twitter_timeline(screenname='SCREENNAME')
```

### User information
```
inca.clients.twitter_userslookup(screen_names=['SNAME1', 'SNAME2', 'SNAME3'])
```
### Followers
```
inca.clients. twitter_followers(screenname='SCREENAME')
```