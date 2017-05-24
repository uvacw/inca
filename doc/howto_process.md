
# How to process data

* We assume you have read the document on "How to scrape" and therefore are familiar with the general way of working with extending INCA*

After scraping your data, you probably want to (pre-)process them. One principle of INCA is to avoid doing things twice, so when doing some preprocessing (like stopword removal or part-of-speech tagging), we store the result as a new key. For instance, if if you have the `text` of a news article you scraped, you might store a lowercased version in a field with the key `text_lowercase`.

## Minimal working example
Let's first start with a simple working example.

```python
p = inca.processing.basic_text_processing.lowercase()
p.run('4329041','text')
```

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
