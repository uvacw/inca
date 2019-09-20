# Importing and exporting data

When running INCA, next to scraping data, processing data, and analyzing data, you probably also want to be able to import and export data to and from other sources. Doing so is necessary for creating backups, but also for working with data you collected in other ways, or for exporting data to work with in other programs or to share with colleagues. 

In this document, we explain some common ways to do so.




## General INCA import/export functions

INCA also has a couple of built-in functions to export to often-used generic formats, especially JSON and CSV.

The way how this works is very straightforward:

```
from inca import Inca
myinca = Inca()

myinca.importers_exporters.export_json_file(query = 'doctype:"daily telegraph"')
```

The query can take any form of a query string as outlined in the [ElasticSearch documentation](https://www.elastic.co/guide/en/elasticsearch/reference/5.5/query-dsl-query-string-query.html#query-string-syntax). Optionally, you can specify a `destination`, otherwise, a folder called `exports` will be created in the current working directory. Alternatively, you can also supply a query in the form of a dict, such as `query = {'query':{'range':{'publication_date':{'gte':2014,'lt':2016}}}}`



Similarly, you can export it as CSV: 
```
myinca.importers_exporters.export_csv(query = 'doctype:"daily telegraph"')
```
You can specify a `delimiter`, such as  `","` or `";"`. Make sure to use ; for compatability with a European locale of Microsoft Excel. Check out the helpfile for more options with `help(myinca.importers_exporters.export_csv)`



Vice versa, you can import a folder with JSON-files into inca with
```
inca.core.database.import_documents('/home/damian/myjsonfiles')
```

**CURRENTLY, IMPORTING DOES NOT WORK. THIS IS A KNOWN BUG AND WILL BE FIXED**





## Specific importers and exporters

#### LEXIS NEXIS
News articles can be downloaded from the Lexis Nexis website as a txt file including a maximum of 200 articles. Not all articles contain the same information or have the same layout. This importer takes each txt file, extracts the information in each article, and yields one dict per article.

The importer always extracts the following information:
- title
- doctype
- text
- publication date
- suspicious (a check whether the article actually contains text)

If present, the importer also extracts:
- category
- byline

The importer is used as follows. The path should be replaced by the path to your folder containing the Lexis Nexis txt file(s):
```
from inca import Inca
myinca = Inca()

myinca.importers_exporters.lnimporter(path="/home/marieke/mylexisnexisfiles")
```


**TO BE ADDED:**
- Timelines



# Backing up the whole INCA database



## INCA backup
INCA has a built-in interface to the backup-and-restore functionality of Elasticsearch:
```
inca.core.database.create_backup()
inca.core.database.restore_backup()
```
This can be useful to create a snapshot and to be able to return to it later on. However, all of this happens within Elasticsearch, so you don't really create a backup file that you can easily share between machines or open with another application.


## Elastic Dump
Elastic Dump is a tool that allows you to dump the content of your whole database (or a selection of it) into a JSON file. It also works the other way round. 

For instance, if you run elasticsearch on your laptop and want to get your data to another laptop or to a server, you can dump the whole datbase into a JSON-file, transmit this file to the other machine, and read it into the database running on that machine.

To use Elastic Dump, you need NodeJS (a framework in which this program is written). You might already have it. Anyhow, it's really easy to install it on Ubuntu:
```
sudo apt install npm
sudo apt install nodejs-legacy
```

After that, you can install Elastic Dump:
```
sudo npm install elasticdump -g
```

To create a full dump of your (local) database into a file, you could for instance run this command:

```
elasticdump --input=http://localhost:9200/inca --output=incathinkpad.json
```
To import data, you can do it the other way round:
```
elasticdump  --input=incathinkpad.json --output=http://localhost:9200/inca
```

Type `elasticdump --help` for more options.


Some example scripts:

### Dumping everything
To create a complete backup, split into several files, and to also backup the original mapping, you could run:

```bash
#!/bin/sh
elasticdump \
    --input=http://localhost:9200/inca6 \
    --output=es-backup20190523/inca6_mapping.json \
    --type=mapping

elasticdump \
    --input=http://localhost:9200/inca6 \
    --output=es-backup20190523/inca6.json \
    --type=data \
    --fileSize=2048mb
```

If you, instead, want to limit yourself to, for instance, a specific time frame, you can specify a query:
```bash
#!/bin/sh
elasticdump \
    --input=http://localhost:9200/inca6 \
    --output=es-backup20190523/inca6_mapping.json \
    --type=mapping

elasticdump \
    --input=http://localhost:9200/inca6 \
    --output=es-dump_april-june/inca6.json \
    --type=data \
    --fileSize=2048mb \
   --searchBody '{ "query": { "range": {  "publication_date": {  "gte": "2019-04",  "lt": "2019-07" }}}}' 
```
