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

- Install Elasticsearch 6.
- Make sure you have the python3-dev package installed (`sudo apt-get install python3-dev`) as well as a c compiler (`sudo apt-get install g++`).
- Then:
```
pip install git+https://github.com/uvacw/inca.git
pip install https://github.com/explosion/spacy-models/releases/download/nl_core_news_sm-2.0.0/nl_core_news_sm-2.0.0.tar.gz
```
