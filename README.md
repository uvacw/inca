# INCA AIMS

INCA aims to provide a bundle of scraping and analysis functionalities for social scientists. The main goals are to facilitate

 1. Data collection from newspapers
 2. Basic processing, such as tokenizing, lematizing
 3. Some analysis such as LDA, K-Means and predictive modelling

# INCA USAGE

INCA is currently under heavy development. local installs are not recommended at this time

## For those brave enough:

1. Install elasticsearch

```
wget https://download.elastic.co/elasticsearch/release/org/elasticsearch/distribution/tar/elasticsearch/2.3.4/elasticsearch-2.3.4.tar.gz
```

2. Unzip it

```
tar -zxvf elasticsearch-2.3.4.tar.gz
```

3. Run it

```
./elasticsearch-2.3.4/sbin/elasticsearch
```

4. Install INCA dependencies (you should probably do this in a virtual environment!)

```
pip install -r Requirements
```

5. Use inca

```
python
import inca
```