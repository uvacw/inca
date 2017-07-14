# Importing and exporting data

When running INCA, next to scraping data, processing data, and analyzing data, you probably also want to be able to import and export data to and from other sources. Doing so is necessary for creating backups, but also for working with data you collected in other ways, or for exporting data to work with in other programs or to share with colleagues. 

In this document, we explain some common ways to do so.

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


## INCA import/export functions
INCA also has a couple of built-in functions to export to often-used generic formats, especially JSON and CSV.

### doctype_export and import_documents
`inca.core.database.export_doctype` exports all items from a specific doctype (e.g., all articles from a specific source) to a series of seperate JSON files. It creates a subdirectory `exports` in which it stores all the articles.
Example:
```
inca.core.database.export_doctype('nu')
```
Vice versa, you can import a folder with such JSON-files into inca with
```
inca.core.database.import_documents('/home/damian/myjsonfiles')
```


### export_csv
`inca.core.database.export_csv()` creates a subdirectory `exports`  in which it stores a CSV table with all items that match a specific ElasticSearch query. You can specify which keys to include as columns in the CSV table. If no keys are given, doctype, publication_date, title, byline, and text are stored.
Example:
```
inca.core.database.export_csv(query = {'query':{'match':{'doctype':'nu'}}}, keys=['publication_date', 'title', 'teaser_rss'])
```