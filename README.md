# INCA AIMS

INCA aims to provide a bundle of scraping and analysis functionalities for social scientists. The main goals are to facilitate

 1. Data collection from websites and social media.
 2. Basic processing, such as tokenizing, lemmatizing, POS-tagging, NER
 3. Some analyses such as machine learning or time series analysis

# INCA USAGE

INCA is currently under heavy development. We cannot guarantee that it works as expected.

## For those brave enough:

Please have a look at the documentation in the `inca/doc/` folder.

... and/or use the following to quickly install inca:

- Make sure you have the Java Runtime environment, because Elasticsearch (see next step) cannot be installed without. On Ubuntu, you can just do `sudo apt-get install default-jre`.
- Install Elasticsearch 6. You can find instructions here: https://www.elastic.co/guide/en/elasticsearch/reference/current/install-elasticsearch.html
- Make sure you have the python3-dev package and the python3-tk package installed (`sudo apt-get install python3-dev python3-tk`) as well as a c compiler (`sudo apt-get install g++`).
- Make sure you have pip3 (`sudo apt install python3-pip`) and setuptools installed (`sudo pip3 install setuptools`)
- Then:
```
pip3 install git+https://github.com/uvacw/inca.git
```

- If you want to use `pattern` for preprocessing, also do:
```
sudo apt-get install libmysqlclient-dev
sudo pip3 install pattern
```