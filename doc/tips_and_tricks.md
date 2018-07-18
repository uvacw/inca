# Easy tips and tricks for starters

In this document, you can find some useful tips and tricks for when you just started the scraping for INCA. Please add anything you find useful to this doc.

## Creating a new branch in Github
Before getting to work, create a new branch. Changes or additions should be made in a separate branch (a copy of the development branch). Later the changes or additions are merged with the development branch through a pull request (after it has been reviewed). Replace fixdocs with the name of your new branch. 
```
cd /home/lisa/inca/inca		# Go the inca directory
git checkout development	# Make sure you are on the development branch (as a basis)
git pull			# Update your files to the latest version of the development branch
git checkout -b fixdocs		# Create a new branch called fixdocs 
```

## How to start INCA

To start INCA, go to your INCA folder and import INCA in python
```
cd /home/lisa/inca
ipython3
from inca import Inca
```
You forgot to run Elastic Search if you receive the follwing warning: _WARNING:INCAcore.database:No databse functionality available_. Start Elastic Search and try again. 
```
sudo service elasticsearch status	# Check whether elasticsearch is running
sudo -i service elasticsearch start	# Start elasticsearch
sudo -i service elastic search stop	# Stop elasticsearch
```

## Opening a file with emacs

Go to the directory where your file is located, and open it with emacs
```
cd /home/lisa/inca/inca/rssscrapers
emacs vlaanderen_scraper.py
```

## Terminal commands

- cd = change directory
   The cd command is used to move into a directory
```
cd /home/lisa/inca	# move into directory
cd ..			# move back one directory
cd ~ 			# move back to the home directory
```

- pwd = print working directory
   The pwd command is used to check which directory you are currently in. 
```
pwd
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
mv vlaanderen_scraper.py /home/lisa/inca/inca/scrapers		# move source to destination
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
The scrapers have to end with _scraper.py

- man = manual
  The man command is used to learn more about a certain command. 
```
man pwd   # replace pwd with any command
```
Other useful tips:
* Press CLTR-C to cancel a command.
* Use the up arrow key to show previous commands. 



## Testing a scraper

To test a scraper, use the save=False option
```
data = myinca.rssscrapers.vlaanderen_scraper.vlaanderen(save=False)
```
Tip: if you don't know the path to your scraper by heart, use the tab (during a word) to let python finish your typing or (after a .) to show you the files in the folder

Now that you have your data, you can test it. 
```
len(data)		# is it an appropriate length?
data[0].keys()		# shows the keys in this element
data[0]['category']	# shows you the value associated with the key
```
If the running didn't work, so there are zero elements in the list, then the problem probably lies with trying to retrieve the rss feed. If there are elements, but not all keys are present, the problem lies with this particular key.

You can also retrieve 1 specific key for a set of elements to check if the scraping worked.
```
for i in range(30):
    try:
        print(data[i]['category']):
    except:
        print('no category')
```

## Testing the parser using a specific article

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

## Help with methods
If you want to find out what a method does or are looking for more options, you can always check out the help file of a method, like so:
```
help(myinca.importers_exporters.export_csv)
```
You can exit the screen by pressing q.



## Pushing to Github
When your scraper is done and tested, the file can be pushed to Github.
```
git status							# check which changes have been made
git add /home/lisa/inca/inca/scrapers/vlaanderen_scraper.py
git commit -m 'explanation'					# replace explanation with an explanation of what you did/added
git push      							# push it to the development branch
```

When you get the error: _fatal: The current branch fixdocs  has no upstream branch._, run the following command (replace fixdocs with your branch name):
```
git push -set-upstream origin fixdocs
```


## Emacs commands
Still has to be done
