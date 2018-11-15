
# How to process data

* We assume you have read the document on "How to scrape" and therefore are familiar with the general way of working with extending INCA*

After scraping your data, you probably want to (pre-)process them. One principle of INCA is to avoid doing things twice, so when doing some preprocessing (like stopword removal or part-of-speech tagging), we store the result as a new key. For instance, if you have the `text` of a news article you scraped, you might want to store a lowercased version in a field with the key `text_lowercase`.

## Minimal working example
Let's first start with a simple working example.

```python
p = myinca.processing.lowercase('nu','text',save=False)
result=next(p)
```

This example runs an (extremely simple) processor that does not do anything else than calling `.lower()` on a string. (You see, it's a toy example).

What happens exactly? The first line creates a generator that processes the field 'text' from all documents with the doctype 'nu'. If we want to get the first processed document, we can just use next(p). Alternatively, we could use a loop:
```python
for result in p:
    print(result)   # or do something more useful
```

Result will contain the original document, with an additional key that contains the processed field.

Other parameters you can use are `save=True` for storing the results to the database, `force=True` for forcing overwriting the content even if it already exists, and `new_key=your_own_key_name` to name the additional key containing the processed field. Additionally, you need to loop over the results to save them:

```python3
p = myinca.processing.lowercase('nu','text', new_key='text_lowercase', save=True)
for result in p:
    pass
```

It is also possible to supply an Elasticsearch query instead of a doctype, which is useful if you only want to process some specific documents. For instance, `_exists_:topic` will process all documents that contain the key 'topic', `text:vvd` will include all documents that include 'vvd' in the key 'text', or `doctype:"nu" AND publication_date:[2018-01-01 TO 2018-12-31]` will process all nu.nl articles published in 2018. More information on Elasticsearch 'Query String Queries' can be read in the [Elasticsearch documentation](https://www.elastic.co/guide/en/elasticsearch/reference/5.5/query-dsl-query-string-query.html#query-string-syntax).

```python3
p = myinca.processing.lowercase('doctype:"nu" AND publication_date:[2018-01-01 TO 2018-12-31]','text', save=True)
for result in p:
    pass
```

Finally, instead of supplying a doctype to apply the processor on, you can also use a generator here (for instance, from the myinca.database.* collection):

```python3
p = myinca.processing.clean_whitespace(myinca.database.doctype_examples('nu'),'text',save=False)
```

```python3
g = myinca.database.document_generator('mark rutte')
p = myinca.processing.clean_whitespace([e for e in g],'text',save=False)    # TODO: It should be possible to feed g directly, need to find out why that fails
```


## Writing your own processors

Just like scrapers are automatically loaded when importing inca, all files with a name ending on `_processing.py` in the folder `processing` are automatically available. Therefore, to write an own processor, you just need to put such a file in that folder. 

All processors inherit from the class Processer, and the only thing you have to modify is their `method process`. All other stuff (like `.run()`, `.runwrap()`, etc. is already inhereted. 

The field you are processing is always denoted as `document_field`, so the processor used above is defined as follows:

```python
class lowercase(Processer):
    '''converts to lowercase'''
    def process(self, document_field):
        '''converted to lowercase'''
        return document_field.lower()
```

Thus, to write your own processor, you only have to modify the `process` function so that it does more than just calling `.lower()` and return.


# Processing images

[This section became obsolete, the image downloader is just a processor like any other processor]