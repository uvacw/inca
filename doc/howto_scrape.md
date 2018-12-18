
# How to scrape web pages

Before we will explain to you how you can scrape in INCA, it is important that you understand some of the terminology that we will be using, and have some knowledge of INCA's structure. In the proceeding, we adress these topics.

## Getting acquainted with terminology: understanding classes, instances, and inheritance. 

By now, you are familiar with some of the more basic data structures in Python, such as lists, strings, etc. ... All of these are also *objects*, but in INCA, we will be working with more complex objects as well.
  * **Class**: a class defines structure - it tells us how someting should be laid out, how new objects should be structured. That is why, often, they are described as blueprints of creating objects. You can also think of it as a logical grouping of both data and methods. 
A class does not, however, usually does not fill in the content. In Python, we define a class with `class`. When dealing with more complicated data structures, classes are very useful. 
  * **Instance** (aka object): An instance is kind of a copy of a class; is the realized version of the class. An instance usually does contain some specific content. Imagine you have written a class called `nuscraper`. If you want to use it, you first create an instance, for example like this: `mylittlescraper=nuscraper()`. From a *single* class you can create *as many instances* as you'd like (each one of them being unique). 
  * **Function**: For a recap, see [Damian's book](http://www.damiantrilling.net/). With regard to the difference between functions and methods, it is important to know that a function is not directly associated to an object. Defined in Python with `def`.
  * **Method**: directly associated with an object. It can only be called from the object. Defined in Python with `def` within a class definition. If you define a function in a class, it becomes a method of every instance of that class. For instance, if the `nuscraper` class contains a function definition named `run`, than each instance (like `mylittlescraper`) has a method `.run` and you can call it with `mylittlescraper.run()`.
    * **Inheritance** If we write a class definition, we don't have to start from scratch. Imagine if we have a class for called `animal`, with some methods `eat`, `sleep` and so on. If we want to create a new class called `cat`, we can start off by saying that a `cat` is an animal, so that we don't have to repeat all of this: `class cat(animal)`. All methods like `eat` and `sleep` are already present then, and we can only have to add additional methods, for example `miaow` - something other animals cannot do.

The concepts of classes and instances can be a bit tricky. This **example** will maybe help you understand it better:

> _Let’s say that the government has a particular tax form that it requires everybody to fill out. 
> Everybody has to fill out the same type of form, but the content that people put into the form differs from person to person. 
> A class is like the form: it specifies what content should exist.
> Your copy of the form with your specific information if like an instance of the class: it specifies what the content actually is._
[Source + more info here](http://www.jesshamrick.com/2011/05/18/an-introduction-to-classes-and-inheritance-in-python/)

In our case, instead of filling out a form we need to extract information of websites. Let's take the example of one specific scraper class, ``nu''. 
The info on *how* to extract this information is contained in the class: What's the XPATH of the title? Where to find the main text? And so on. All of this is specified within functions in the class. But the class itself cannot be run; and the specific articles we want to process change every day. 
If we want to run this scraper, we create a specific instance and run it.


## Understanding the structure of INCA.

To better understand some of the classes, methods, and functions we will be using, it is important to 
know that INCA consists of several layers. At the heart of INCA (the core), several classes are defined that regulate the
importing and handling of data. For example, here we find a file that tells inca what a scraper is: i.e., the class for scrapers: `class Scraper(Document):`
Most students and assistants will **only** be working on the **outer shell** of INCA. This is where you, for example, find 
several web scrapers. As we will be working in this 'outer shell' of INCA, we do not have to bother about some of the most 
fundamental - yet very complicated - code that is at the core of INCA. 

We will, however, make use of the methods and functionalities that are defined at INCA's core. 
More specifically, we will *inherit* from pre-defined classes. In fact, each scraper that we will be writing should inherit from the class `Scraper` (or from the class `rss`, which inherents from `Scraper` itself).

## Writing a scraper

### 1. Scrapers for webpages with RSS feed
We start with explaining how to write a scraper for rss website. Technically, you are not scraping the pages with an rss feed. 
The `get` method of the `class rss` already retrieves the html source of the rss page you aim to parse. That's why inheritance is such a cool thing; 
it saves a lot of work! You will only write code that will parse the content. 

Clone a version of INCA and start working in the file news_scrapers.py (note: if you are not making a scraper for a rss feed page, please make a new .py file). 
Just add your own code below the rest of the code. Write the code based on examples from already existing scrapers. 

Below, we explain how you can write a scraper with the example of the ad scraper(i.e., `ad (www)`).

1.	In the first line, you write:

```python
1.class ad(rss):
2.    """Scrapes ad.nl"""
3.
4.def __init__(self):
5.    self.doctype = "ad (www)"
6.    self.rss_url='http://www.ad.nl/rss.xml'
7.    self.version = ".1"
8.    self.date = datetime.datetime(year=2018, month=5, day=16) 
```

**line 1**

`class` indicates that we create a class. `ad` is the name for the class. `(rss)` refers to the class from which `ad` is inheriting. 

**line 2**

denote with double ` """` what the class does: in this case, it scrapes ad.nl. This is called a *docstring* and enables us to, for example, automatically create a help function.

**lines 4 - 9**

When creating a new scraper, we need to initialise it. More specifically, we need specify what kind of scraper we are writing. This happens is lines 4 - 9. 
The `__init__(self):`  method is a special kind of method that is called whenever an instance of a class is created. 
the `self` variable represents the instance of the object (Think of referring to 'self' as to referring to the specific instance that we have created, not to the abstract class). 
As we can have multiple instances (nothing prevents someone from running the scraper multiple times), referring to `self` allows us to do something with the specific instance rather than with all ad-scrapers.

Consequently, we have to define the following:
`self.doctype = "ad (www)` --> fill in the name of your scraper.
`self.rss_url='http://www.ad.nl/rss.xml'` --> fill in the address of the rss-feed of your scraper.
`self.version = ".1"` --> give the version of the scraper (in case you have adjusted the scraper, you can change this here.
`self.date    = datetime.datetime(year=2018, month=5, day=16)` --> provide the date you last adjusted the scraper. 

```python
10.   def parsehtml(self,htmlsource):
11.        '''
12.        Parses the html source to retrieve info that is not in the RSS-keys
13.        In particular, it extracts the following keys (which should be available in most online news:
14.        section    sth. like economy, sports, ...
15.        text        the plain text of the article
16.        byline      the author, e.g. "Bob Smith"
17.        byline_source   sth like ANP
18.
19.        '''
20.        try:
21.            tree = fromstring(htmlsource)
22.        except:
23.            logger.warning("Could not parse HTML tree",type(doc),len(doc))
24.            return("","","", "")
25.        try:
26.            category = tree.xpath('//*[@class="container"]/h1/text()')[0]
27.        except:
28.            category=""
29.            logger.debug("Could not parse article category")
30.        #1. path: regular intro                                                                                                    
31.        #2. path: intro when in <b>; found in a2014 04 130                                                                         
32.        textfirstpara=tree.xpath('//*[@id="detail_content"]/p/text() | //*[@class="intro"]/b/text() | //*[@class="intro"]/span/text() | //*/p[@class="article__intro"]/text() | //*/p[@class="article__intro"]/span/text()')
33.        if textfirstpara=="":
34.            logger.info("OOps - geen eerste alinea?")
35.        #1. path: regular text                                                                                                     
36.        #2. path: text with link behind (shown in blue underlined); found in 2014 12 1057                                          
37.        #3. path: second hadings found in 2014 11 1425   
38.        textrest = tree.xpath('//*/p[@class="article__paragraph"]/text() | //*[@class="article__paragraph"]/span/text() | //*[@id="detail_content"]/section/p/a/text() | //*[@id="detail_content"]/section/p/strong/text() | //*/p[@class="article__paragraph"]/strong/text()')
39.        if textrest=="":
40.            logger.warning("Could not parse article text")
41.        text = "\n".join(textfirstpara) + "\n" + "\n".join(textrest)
42.        try:
43.            author_door = tree.xpath('//*[@class="author"]/text()')[0].strip().lstrip("Bewerkt").lstrip(" door:").lstrip("Door:").strip()
44.        except:
45.            author_door=""
46.        if author_door=="":
47.            try:
48.                author_door = tree.xpath('//*[@class="author"]/a/text()')[0].strip().lstrip("Door:").strip()
49.            except:
50.                author_door==""
51.        if author_door=="":
52.            try:
53.                author_door=tree.xpath('//*[@class="article__source"]/span/text()')[0].strip().lstrip("Door:").strip()
54.            except:
55.                author_door=""
56.                logger.debug("Could not parse article source")
57.        try:
58.            brun_text = tree.xpath('//*[@class="author"]/text()')[1].replace("\n", "")
59.            author_bron = re.findall(".*?bron:(.*)", brun_text)[0]
60.        except:
61.            author_bron=""
62.        text=polish(text)
63.
64.        extractedinfo={"category":category.strip(),
65.                       "text":text.strip(),
66.                       "byline":author_door.replace("\n", " "),
67.                       "byline_source":author_bron.replace("\n"," ").strip()
68.                       }
69.
70.        return extractedinfo
```

**lines 10 - 17**

Next, you are defining the method `parsehtml`. You provide the argument `self`, as the method 
has to be able to address its specific instance. The argument `htmlsource` that is passed on is already provided by the functions defined in the parent class `class rss`. It's just a string of HTML code.

As can be seen in 11 - 17, We want to parse the html source to obtain: **section, text, byline and byline_source**. 

Please read Damians chapter on XPATHs to refresh your memory. 

Some handy shortcuts for modifying the xpaths:
  * remove `x:` (you might want to substitute with / if needed)
  * add `text()` at the end of you xpath to show the text. 
  * replace `id(<whatever>)` with `//`

You might want to play around with looking up the xpath, showing the source code, or saving the page in html format. 

**lines 64 - 70**
It does not really matter how you arrive at xpath you are including, as long as you, in the end, succeed in retrieving the extracted info. 


#### WARNINGS
If you define a method with a name that already exists within INCA, you run the risk of overwriting
existing methods. We don't want that. Please do not overwrite the following methods: run(), _test_function(),  

For example, never write a method using:
```
 def run(self,<whatever>):
 ```
When you write a scraper for an RSS-based website, just inherit the functionalities that are already defined by the class rss. In addition, we can write our own methods.

In fact, `(rss)` refers to a class defined in the core of inca: `class rss(Scraper)`. 

## Testing your code

### Testing your code

As mentioned, it is important to test your scraper before pushing it to github. 
You can test your scraper on your own system before pushing it. Start Python3 in your terminal (or IDE, what you want),
and import inca. Please note: you do not have to activate Elastic Search for this (as you are just testing the materials).
Hence, be prepared to recieve the following warnings:]

_WARNING:INCAcore.database:No database functionality available. This means you will not be able to SAVE the results of any scraper or processor!_
_WARNING:processing.basic_text_processing:Pattern is NOT python 3 compatible...skipping_

When running a scraper, please give the argument `save = False`, as you just want to work with test data.

```python
import inca
myinca = inca.Inca()
data = myinca.rssscrapers.nu(save=False)
```

Now, you can start playing around with the data (`r`).

Please note that you have tab completion (this will show you all the methods inside myscraper)!

```python
len(r)  # check how many articles you scraped.
r[0].keys() #this will give you all the info you need about the existing keys 
r[0]['text'] # or use different key of course, such as:
r[0]['title']
```

### Testing xpaths in ipython

You can also test and adjust your xpaths directly and interactively in Python. This can be helpful, because it allows you to immediately see whether your xpath actually produces any output. 

For this, make sure you have iPython (or Python) running. `import inca` and run your scraper (as illustrated above). Now, type the following:


```Python
from lxml.html import fromstring

tree = fromstring(r[0]['htmlsource']) # this grasps the htmlsource of the first item you just scraped (r[0]). Of course, you can also select the second(r[1])... etc. 
```
now, you can just start testing your xpaths in the following manner:

```Python
tree.xpath('<putyourxpathhere') # for example: tree.xpath('//*[@class="article-header-title"]/text()')
```

Now, you will see whether you xpath actually produced the desired content or not. If needed, you can adjust the xpath, play around with cleaning the output, etc 

### Use logging for debugging

While writing a scraper, you maybe use a lot of `print()` functions to watch what is going on while testing them. However, before finalizing your scrapers and issuing a Pull Request, please remove all printing so that scraping can run silently in the background.

A good alternative is making use of the logger instead of printing. You can choose between (in decreasing order of importance of the message):

```python
logger.critical("Here is some message")
logger.error("Here is some message")
logger.warning("Here is some message")
logger.info("Here is some message")
logger.debug("Here is some message")
```

By default, only messages that are 'warning' or more important are shown. But you can change this. For instance, if you want to see all messages that are of level debug or higher, just do:

```python
myinca = inca.Inca(verbose=True)
# or even:
myinca = inca.Inca(debug=True)
```

A good way of using logging when writing scrapers can be:

- emit an error when scraping fails
- emit a warning when something unexpected of significance happens: Specifically, include warnings when the scraper fails to parse the HTML tree, the title and the text 
- emit an info when, e.g., an element does not contain an expected field (if not important enough for a warning)
- emit a debug for very detailed steps (e.g., the URL being fetched, parsing category, parsing source, parsing source byline)


### Scrapers for webpages without RSS feed

The big advantage of an RSS scraper is that the RSS feed already provides you with a list of URLs. Therefore, the only thing to do is to write a function that parses the content behind these links.

In contrast, for a generic scraper, you need to do all this yourself. As this is highly site-dependend, we'll only outline the general approach here. Please look at some existing scrapers for examples.

1. Choose a starting page (e.g., the homepage) and parse all links to relevant items.

2. If necessary, repeat (1) for more pages (e.g., 'next items', `?page=2', ...)

3. Loop over the list of URLs, download them, parse them.

Make sure that you have some limits installed to avoid that the scraper continues infinitely.


There is also a way to have INCA check whether an item with the same URL already exists to avoid getting multiple entries when running non-RSS scrapers as a cronjob (see below).
Consider this example:

```python3
myinca.scrapers.groenlinks(startpage=1, maxpages=1)
myinca.database.list_doctypes()
```
If you run this code twice, then you will see that you have the press releases twice in there. To prevent this, you can use the `check_if_url_exists` argument:

```python3
myinca.scrapers.groenlinks(startpage=1, maxpages=1, check_if_url_exists = True)
```



## How to put scrapers into production
After having written and tested your scrapers, you probably want to put them into production - i.e., want to run them automatically on a regular basis. In this section, we describe how to do so on a typical Linux (Ubuntu) system. On MacOS, this should work roughly similarly.

0. Make sure ElasticSearch is installed and running (see [Getting Started](gettingstarted.md))

1. Write a python script that runs all desired scrapers in a row. INCA comes with an example script for this purpose: `scrapejob.py`. Edit it to fit your purposes.

2. Make sure that the script is executable: `chmod u+x scrapejob.py`

3. Create a shell script that runs this python script. For instance, you could create a file `/home/damian/scrape.sh` with the following content: 
```
#!/bin/bash
cd /home/damian/inca-prod/inca
./scrapejob.py
```

4. Make the shell script executable as well, using `chmod u+x scrape.sh`.

5. Add a cronjob to your crontab by executing `crontab -e`. The following line would run your scrapers at 15 minutes past every hour:
`15 * * * * /home/damian/scrape.sh`

6. You are done! However, in order to be able to check whether everything works properly, it is advisable to install Kibana, a graphical dashboard that allows you exploring the data you are scraping. You can do so as follows:
- Install Kibana with `sudo apt install kibana`
- Run Kibana with `sudo service kibana start`
- Open a web browser and access Kibana by browsing to `http://localhost:5601`
- You are asked to configure an index pattern. Set the index pattern to a simple `*` and select that you do not want to use a Time filter.
- Configure visualizations and dashboards.


