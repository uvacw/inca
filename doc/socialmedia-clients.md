# How to use social media APIs

This is a first draft for a tutorial on how to connect to social media APIs with INCA.

We give the example of Twitter, for Youtube, it basically works the same way. Use tab completion and you'll see ;-)

## Instantiating Inca
```
from inca import Inca 
myinca = Inca()
```

## Creating an app for Twitter
App needs to be created once. If no name used, info will be stored in the default app.
```
myinca.clients.twittercreateapp()
myinca.clients.twittercreatecredentials()
```

## Collecting Twitter data

### By username (timelines)
```
myinca.clients.twitter_timeline(app='default', screenname='SCREENNAME')
```

### User information
```
myinca.clients.twitter_users_lookup(app='default', screen_names=['SNAME1', 'SNAME2', 'SNAME3'])
```
### Followers
```
myinca.clients. twitter_followers(app='default', screenname='SCREENAME')
```