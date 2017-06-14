# Easy tips and tricks for starters

In this document, you can find some useful tips and tricks for when you just started the scraping for INCA. Please add anything you find useful to this doc.

## How to start INCA

To start INCA, go to your INCA folder and import INCA in python
```
cd /home/lisa/INCA/inca
ipython3
import inca
```

## Opening a file with emacs

Go to the directory where your file is located, and open it with emacs
```
cd /home/lisa/INCA/inca/scrapers
emacs vlaanderen_scraper.py
```

## Terminal commands

- cd = change directory
   The cd command is used to move into a directory
```
cd /home/lisa/INCA	# move into directory
cd ..			# move back one directory
cd ~ 			# move back to the home directory
```

- rm = remove
   The rm command removes files or directories 
```
rm vlaanderen_scraper.py	# delete file
```

- mv = move
   The mv command is used to move or rename files
```
mv vlaanderen_scraper.py newname_scraper.py			# rename file
mv vlaanderen_scraper.py /home/lisa/INCA/inca/scrapers		# move source to destination
```

- cp = copy
   The cp command is used to make copies of files and directories
```
cp vlaanderen_scraper.py			# copy file
cp vlaanderen_scraper.py mycopy_scraper.py	# copy file into different name	
```

- ls = list
  The ls command lists the contents of a directory
```
ls
```
* The scrapers have to end with _scraper.py

## Testing a scraper

To test a scraper, it has to be placed into an object and run.
```
s = inca.scrapers.vlaanderen_scraper.vlaanderen(database=False)
data = s.run()
```
Tip: if you don't know the path to your scraper by heart, use the tab (during a word) to let python finish your typing or (after a .) to show you the files in the folder

Now that you have your data, you can test it. 
```
len(data)		# is it an appropriate length?
data[0].keys()		# shows the keys in this element
data[0]['category']	# shows you the key
```
If the running didn't work, so there are zero elements in the list, then the problem lies with trying to retrieve the rss feed. If there are elements, but not all keys are present, the problem lies with this particular key.

You can also call 1 key for a set of elements to check if the scraping worked.
```
for i in range(30):
    try:
        print(data[i]['category']):
    except:
        print('no category')
```

## Scraping using a specific article

If some of the keys didn't work, you can use the htmlsource of one of the articles in your dataset to try to find the right xpaths for these keys. Try out different xpaths to find what you're trying to scrape.
```
from lxml.html import fromstring
tree = fromstring(data[0]['htmlsource'])
tree.xpath('//[@class="author"]/text()')   
```
Of course, this method can also be used when you don't have a dataset yet (when you just started a new scraper) or when you want to try a specific article online. This can be done by saving the html code from that specific article. Click right on the article to save the page as an html only webpage. See bottom right in the save menu to click the option 'web page, HTML only'. This htmlsource can then be placed into the tree object, after which it can be tested.
* Note: this works for Firefox, not sure about other browsers
```
from lxml.html import fromstring
htmlsource = open('/home/lisa/Downloads/test.html').read()
tree = fromstring(htmlsource)
```
## Pushing to Github
When your scraper is done and tested, the file can be pushed to Github.
```
git add /home/lisa/INCA/inca/scrapers/vlaanderen_scraper.py
git commit -m 'added category'					# use commit to explain what you did/added
git push
```

## Emacs commands
Still has to be done
