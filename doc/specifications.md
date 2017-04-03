# Specifications

This file collects the specifications we use for developing INCA. Think of, for instance, the key-value pairs a scraper returns, or the arguments a processor accepts.

## Scrapers

Scrapers are expected to return the following keys:

key|data type|description|example|mandatory?
--------------------------------------------
doctype|string|source of the document|nu, nrc, kamervraag|yes
publication_date|datetime object|date (optionally: time) of publication|datetime(2017,4,1)|yes
text|string|The full (plain!) text of the document, excluding title etc.|Bij een explosie in een metro in het Russische Sint-Petersburg zijn maa...|yes
byline|string|author|Jan Jansen|no
category|string|in case of news: section|economy, sports|no
feedurl|string|in case of rss-feed: url of feed|http://www.nu.nl/rss|no
htmlsource|string|the raw html code|<http><header>...|yes
teaser|string|in case of rss-feed: teaser that is distributed via feed. Otherwise, if appicable: Teaser as used on some overview page|Bij een explosie in een metro in het Russische Sint-Petersburg zijn maa...|no
title|string|title of the document|Explosie in Sunt-Petersburg|yes
url|string|source url of the item|http://www.nu.nl/buitenland/4590777/zeker-tien-doden-bij-explosie-in-metro-sint-petersburg.html|yes

In principle, extra fields can be added, but this should be documented. Candidates for inclusion:

key|data type|description|example|mandatory?
--------------------------------------------
likes_int|int|number of likes,thumbs up etc|42|no
dislikes_int|int|number of thumbs down etc|42|no
shares_int|int|number of shares|42|no
replies_int|int|number of replies|42|no
