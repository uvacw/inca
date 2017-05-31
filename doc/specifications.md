# Specifications

This file collects the specifications we use for developing INCA. Think of, for instance, the key-value pairs a scraper returns, or the arguments a processor accepts.

## Scrapers

Scrapers are expected to return the following keys:
Changes are in **bold**

key | data type | description | example | mandatory?
--------|-------|--------|--------|---------------------
_id | string | unique id. In case of RSS: use post.id as _id to enable checking whether we already got that article | ewghwu4buwoe, www.nu.nl/-/585605 | no (in case of rss: yes)
doctype | string | source of the document | nu, nrc, kamervraag | yes
publication_date | datetime object | date (optionally: time) of publication | datetime(2017,4,1) | yes
text|string|The full (plain!) text of the document, excluding title etc.|Bij een explosie in een metro in het Russische Sint-Petersburg zijn maa...|yes
byline|string|author|Jan Jansen|no
bylinesource|string|some newssites give both a journalist's name (to be stored in `byline`) and also the original source of the material (like a press agency), which can be stored here|ANP|no
category|string|in case of news: section|economy, sports|no
feedurl|string|in case of rss-feed: url of feed|http://www.nu.nl/rss |no
htmlsource|string|the raw html code|`<http><header>...`|yes
**teaser**|string|Teaser, usually some short paragraph between title and text. Only some outlets have this|Bij een explosie in een metro in het Russische Sint-Petersburg zijn maaandag twee mensen om het leven gekomen.|no
**teaser_rss**|string|Teaser that is distributed via feed. |Bij een explosie in een metro in het Russische Sint-Petersburg zijn maa...|yes (for rss)
**title**|string|title of the document (as scraped from HTML). If there is a subtitle, dive it by newline|Explosie in Sint-Petersburg|yes
**title_rss**|string|title of the document (as retrieved from rss feed)|Explosie in Sint-Petersburg|yes (for rss)
url|string|source url of the item|http://www.nu.nl/buitenland/4590777/zeker-tien-doden-bij-explosie-in-metro-sint-petersburg.html |yes
images|list of dicts|Ordered list (top to down, left to right) of *editorial* images (thus, no navigation and no ads). Each image has the keys url, width, height, caption, source (the photographer and/or press agency), alt (the alt text), href | ... | (still to be implemented)



In principle, extra fields can be added, but this should be documented. Candidates for inclusion:

key|data type|description|example|mandatory?
-------|------|----------|----------|-----------
likes_int|int|number of likes,thumbs up etc|42|no
dislikes_int|int|number of thumbs down etc|42|no
shares_int|int|number of shares|42|no
replies_int|int|number of replies|42|no
imageurls|list of strings|a list of links to relevant images, like photos in a news article|\["http://media.nu.nl/m/7mlxhgda2r7r_wd640.jpg/zeker-tien-doden-bij-explosie-in-metro-sint-petersburg.jpg", "http://www.nu.nl/120381/video/metrostation-sint-petersburg-vol-met-rook-na-explosie.html"] | no
paywall | bool | True if article is fully scraped, but was behind paywall | True | no
paywall_na | bool | True if full text of the article is not available because it was behind a paywall and we didn't have access (e.g., NRC 2015| True | no


Still to discuss: How to deal with comments associated with a news article?



## Processors
Processors accept the following arguments: ...
They return a dict with the modified document, unless .... is specified, in which case the result is stored in the database.
...
...



# Old datamodel until May 2016

## Scrapers

Scrapers are expected to return the following keys:

key | data type | description | example | mandatory?
--------|-------|--------|--------|---------------------
_id | string | unique id. In case of RSS: use post.id as _id to enable checking whether we already got that article | ewghwu4buwoe, www.nu.nl/-/585605 | no (in case of rss: yes)
doctype | string | source of the document | nu, nrc, kamervraag | yes
publication_date | datetime object | date (optionally: time) of publication | datetime(2017,4,1) | yes
text|string|The full (plain!) text of the document, excluding title etc.|Bij een explosie in een metro in het Russische Sint-Petersburg zijn maa...|yes
byline|string|author|Jan Jansen|no
bylinesource|string|some newssites give both a journalist's name (to be stored in `byline`) and also the original source of the material (like a press agency), which can be stored here|ANP|no
category|string|in case of news: section|economy, sports|no
feedurl|string|in case of rss-feed: url of feed|http://www.nu.nl/rss |no
htmlsource|string|the raw html code|`<http><header>...`|yes
teaser|string|in case of rss-feed: teaser that is distributed via feed. Otherwise, if appicable: Teaser as used on some overview page|Bij een explosie in een metro in het Russische Sint-Petersburg zijn maa...|no
title|string|title of the document|Explosie in Sunt-Petersburg|yes
url|string|source url of the item|http://www.nu.nl/buitenland/4590777/zeker-tien-doden-bij-explosie-in-metro-sint-petersburg.html |yes

In principle, extra fields can be added, but this should be documented. Candidates for inclusion:
