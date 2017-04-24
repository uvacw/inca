
# How to scrape web pages

Before we will explain to you how you can scrape in INCA, it is important that you understand some of the terminology that we will be using,
and have some knowledge of INCA's structure. In the proceeding, we adress these topics.

## Getting acquainted with terminology: understanding classes, instances and inheritance. 

By now, you are familiar with some of the more basic data structures in Python, such as lists, strings.. In INCA, we will be working with more complex data structures:
  * **Class**: a class defines structure - it tells us how someting should be laid out, how data should be structured. That is way, often, they are described as blueprints of creating objects. It is a logical grouping of both data and methods. 
It does not, however, fill in the content. In Python we define a class with `class`. When creating more complicated data structures, classes are very useful. 
  * **Instance** (aka object): An instance is a copy of a class; is the realized version of the class. An instance does contain content. 
Instances have the structure of the class but that the values within an instance may vary from instance to instance. From a *single* class you can create *as many instances* as you'd like (each one of them being unique). 
  * **Function**: For a recap, see [Damian's book](http://www.damiantrilling.net/). With regard to the difference between functions and methods, it is important to know 
that a function is not directly associated to a variable/ object. Defined in Python with `def`.
  * **Method**: directly associated to a variable. it can only be called from the object. Defined in Python with `def`. 

As with functions, some methods are build in (i.e., build-in methods), while others are defined by users (i.e., user-defined methods).

The concepts of classes and instances can be a bit tricky. This **example** will maybe help you understand it better:

> _Let’s say that the government has a particular tax form that it requires everybody to fill out. 
> Everybody has to fill out the same type of form, but the content that people put into the form differs from person to person. 
> A class is like the form: it specifies what content should exist.
> Your copy of the form with your specific information if like an instance of the class: it specifies what the content actually is._
[Source + more info here](http://www.jesshamrick.com/2011/05/18/an-introduction-to-classes-and-inheritance-in-python/)


In our case, instead of filling out a form we need to extract information of websites. For each website, we need the same information, but the content will differ 
from webpage to webpage and from article to article [--> klopt dit Damian?]

## Understanding the structure of INCA.

To better understand some of the classes, methods and functions we will be using, it is important to 
know that INCA consists of several layers. At the heart of INCA (the core), several classes are defined that regulate the
importing and classification of data. For example, here we find a file that tells inca what a scraper is: i.e., the class for scrapers: `class Scraper(Document):`
Most students and assistants will **only** be working on the **outer shell** of INCA. This is where you, for example, find 
several web scrapers. As we will be working in this 'outer shell' of inca, we do not have to bother about some of the most 
fundamental -yet very complicated - code that is at the core of INCA. 

We will, however, make use of the methods and functionalities that are defined at INCA's core. 
More specifically, we will inherit from pre-defined classes. In fact, each scraper that we will be writing should inherit from the class `class Scraper(Document):`

## Writing a scraper

### 1.	Scrapers for webpages with RSS feed
We start with explaining how to write a scraper for rss website. Technically, you are not scraping the pages with an rss feed. 
The `get` method of the `class rss` already retrieves the html source of the rss page you aim to parse. That's why inheritance is such a cool thing; 
it saves a lot of work! You will only write code that will parse the content. 

Clone a version of INCA and start working in the file news_scrapers.py. Forgot how? Find it [here](
@damian: instructies van bob zijn anders. hij zegt; new file beginnen for een nieuwe scraper 
https://github.com/uvacw/inca/blob/development/doc/Contributing%20Code%20Guide.md --> nummer 2. 

Just add your own code below. 
Write the code based on examples from already existing scrapers. 

Below, we explain how you can write a scraper with the example of the ad scraper(i.e., `ad (www)`).

1.	In the first line, you write:

```python
1.	class ad(rss):
2.	"""Scrapes ad.nl"""
3.
4.	def __init__(self,database=True):
5.    self.database = database
6.    self.doctype = "ad (www)"
7.    self.rss_url='http://www.ad.nl/rss.xml'
8.    self.version = ".1"
9.    self.date = datetime.datetime(year=2016, month=8, day=2) 
```

**line 1**

`class` indicates that we create a class. `ad` is the name for the class. `(rss)` refers to the class from which `ad` is inheriting. 
**line 2**

denote with double ` """` what the class does: in this case, it scrapes ad.nl. 
**lines 4 - 9**

When creating a new scraper, we need to initialise it. More specifically, we need specify what kind of scraper we are writing. This happens is lines 4 - 9. 
The `__init__(self, database=True)):`  method is a special kind of method that is called whenever an instance of a class is created for the first time. 
the `self` variable represents the instance of the object (it tells Python basically that the method should be applied to the 'self', to the instance that we have created). 
As our instance can have different values, we use `self` instead of `ad`.

---------------------------------------------------------------------------------------

@damian: dit staat in die code van Bob, maar komt niet overeen met initialization in het document news_scrapers.py..


Scrapers should yield dicts that contain the document (news article,
tweet, blogpost, whatever)
For the following keys, please provide the information specified below:
doctype             : The medium or outlet (e.g. volkskrant, guardian, economist)
url                 : URL from which data is scraped (e.g. volkskrant.nl/artikel1)
publication_date    : Date of publication of article/website as specified by outlet, NOT SCRAPING
text                : Plain (no code/XML or HTML tags) text content
OPTIONAL, BUT RECOMMENDED
_id       : a unique, preferably same as external source identifier of the document (e.g. ISBN, DOI )
language  : If you can safely assume the language of specified documents, please specify them here
-------------------------------------------------------------------------------------


Consequently, we have to define the following:
`self.data = database` --> this is always the same. 
`self.doctype = "ad (www)` --> fill in the name of your scraper.
`self.rss_url='http://www.ad.nl/rss.xml'` --> fill in the rss.xml of your scraper.
`self.version = ".1"` --> give the version of the scraper (in case you have adjusted the scraper, you can change this here.
`self.date    = datetime.datetime(year=2016, month=8, day=2)` --> provide the date you last adjusted the scraper. 

```python
10.   def parsehtml(self,htmlsource):
11.        '''
12.        Parses the html source to retrieve info that is not in the RSS-keys
13.        In particular, it extracts the following keys (which should be available in most online news:
14.        section    sth. like economy, sports, ...
15.        text        the plain text of the article
16.        byline      the author, e.g. "Bob Smith"
17.        byline_source   sth like ANP
18.        '''
19.        try:
20.            tree = fromstring(htmlsource)
21.        except:
22.            print("kon dit niet parsen",type(doc),len(doc))
23.            print(doc)
24.            return("","","", "")
25.        try:
26.            category = tree.xpath('//*[@class="container"]/h1/text()')[0]
27.        except:
28.            category=""
29.            logger.info("No 'category' field encountered - don't worry, maybe it just doesn't exist.")
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
40.            logger.info("OOps - empty textrest")
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
56.                logger.info("No 'author (door)' field encountered - don't worry, maybe it just doesn't exist.")
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
should refer to the instance that is defined later on. `htmlsource` is defined in the `class rss`. 
As can be seen in 11 - 17, We want to parse the html source to obtain: **section, text, byline and byline_source**. 

Please Damians chapter on xpath to refresh your memory. 

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

For example, never compile a method using:
```
 def run(self,<whatever>):
 ```

When writing scrapers, you should know that we will work in the 
When you write a scrape for an RSS-based website, please place rss. In this way, you will inherit the 
functionalities that are already defined by the class rss. In addition, we can write our own methods.

In fact, `(rss)` refers to a class defined in the core of inca: `class rss(Scraper)`. 

## 5. Testing

As mentioned, it is important to test your scraper before pushing it to github. 
You can test your scraper on your own system before pushing it. Start Python3 in your terminal (or IDE, what you want),
and import inca. Please note: you do not have to activate Elastic Search for this (as you are just testing the materials).
Hence, be prepared to recieve the following warnings:]

_WARNING:INCAcore.database:No database functionality available_
_WARNING:processing.basic_text_processing:Pattern is NOT python 3 compatible...skipping_

Please give the argument `database = False`, as you just want to work with test data.

```python
import inca
myscraper = inca.scrapers.news_scraper.nu(database=False)  # We do not pass any argument to the __init__ method
r = myscraper.run()
```

In this example, we have created an instance of the class `inca.scrapers.news_scraper.nu` and called it `myscraper`. 
We can now pay around with the methods of the class `inca.scrapers.news_scraper.nu`. For example, we can run the scraper to get some actual data to play around with. 

now, you can start playing around with the instance `r`. 

for example, if you define an object r and assign it mijnscraper, you can now call the methods that are inside 
`inca.scrapers.news_scraper.nu.`

Please note that you have tap completion (this will show you all the methods inside myscraper)

```
len(r)  # check how many articles you scraped.
r[0].keys() #this will give you all the info you need about the existing keys 
r[0]['text']
# of andere keys dus
