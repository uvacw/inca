
# How to process data

* We assume you have read the document on "How to scrape" and therefore are familiar with the general way of working with extending INCA*

After scraping your data, you probably want to (pre-)process them. One principle of INCA is to avoid doing things twice, so when doing some preprocessing (like stopword removal or part-of-speech tagging), we store the result as a new key. For instance, if if you have the `text` of a news article you scraped, you might store a lowercased version in a field with the key `text_lowercase`.

## Minimal working example
Let's first start with a simple working example.

```python
p = inca.processing.basic_text_processing.lowercase()
p.run('4329041','text')
p.run('http://www.nu.nl/-/4801569/','title')
```
Note that the id of a document can take very different forms, depending on the configuration of the scraper. It doesn't necessarily have any inherent meaning.

Tip: If you just want to get some ID of some document for testing, use this function call: 
```python
inca.core.search_utils.doctype_last('nu')[0]['_id']
```
It gives you the id of the last article of type 'nu' that's in the database.

This example instantiates a (extremely simple) processor that does not do anything else than calling `.lower()` on a string. (You see, it's a toy example).
You can then run this processor on some document from the database (in this example, the document with the id '4329041'. It will return a document with a new key called 'text_lowercase' that contains the lowercased version of the string.

## Processing multiple articles
You can use the .runwrap() methods to automatically process multiple documents, for example all articles from nu.nl. If you want to use another name for the new key, you can specify it.
This returns a generator that you can iterate (loop) over:

```python
newdocuments = [e for e in p.runwrap('nu',field='text',new_key='textLC')]
```

Other parameters you can use are `save=True` for storing the results to the database and `force=True` for forcing overwriting the content even if it already exists.



## Writing your own processors

Just like scrapers are automatically loaded when importing inca, all files with a name ending on `_processing.py` in the folder `processing` are automatically available. Therefore, to write an own processor, you just need to put such a file in that folder. 

All processors inherent from the class Processer, and the only thing you have to modify is their `method process`. All other stuff (like `.run()`, `.runwrap`, etc. is already inhereted. 

The field you are processing is always denoted as `document_field`, so the processor used above is defined as follows:

```python
class lowercase(Processer):
    '''converts to lowercase'''
    def process(self, document_field):
        '''converted to lowercase'''
        return document_field.lower()
```

Thus, to write your own, you only have to modify the `process` function so that it does more than just calling `.lower()` and return.


# Processing images

Next, we discuss how you can process images with the image-processor. 
Images are not scraped simultaneously with text. We can retrieve them locally with the image processor. 

Before we start, make sure you have imagehash installed (`pip3 install imagehash`).


## STEP 1: Getting started


First, we have to change the path to where inca will store the images locally. 
Go in your terminal to your inca folder, can type the following:

```
inca admin$ cat default_settings.cfg 
```

Change imagepath to a convient local location. 

Additionally, make sure elasticsearch is on. 


## STEP 2: Scraping some news articles from which we want the images. 

Next, you have scrape some content. 
In this example, we will scrape nu.nl. 
Make sure the database is on (`True`).

```python
myscraper = inca.scrapers.news_scraper.nu(database=True)
r = myscraper.run()
```

Now that we have some articles from NU.nl in our database, we can start retrieving images. 
Let's say, we want the image from the first article we retrieved. Run the following command:

```python
inca.core.search_utils.doctype_last('nu')[0]['_source']['images']
```

This will give you the both the header (`'ALT'`), as the URL (`'URL'`) of the image.

The following command will give you all available keys, as well as the content of the article: 

```python
inca.core.search_utils.doctype_last('nu')[0]
```
For now, we are mainly interested in the article's id, as we need it later.

```python
inca.core.search_utils.doctype_last('nu')[0]['_id']
```
The output is - in this case - : 'http://www.nu.nl/-/4891448/'

## STEP 3: Retrieving and storing images
 
Now, we want to retrieve the images and save them locally. Hence, we will make an instance of the 
`inca.processing.download_images()` class. Then, we will run the instance on the NU-article that we just scraped. 


```python
p = inca.processing.image_processing.download_images()
p.run('http://www.nu.nl/-/4891448/','images')
```
Now, go to your local folder that you specified in step 1 to find your image(s). 

