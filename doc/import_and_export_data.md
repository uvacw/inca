# Importing and exporing data

bla
bla
bla

## Elastic Dump

sudo apt install npm
sudo apt install nodejs-legacy



(want NodeJS)

sudo npm install elasticdump -g


elasticdump --input=http://localhost:9200/inca --output=incathinkpad.json

en andersom terug:

elasticdump  --input=incathinkpad.json --output=http://localhost:9200/inca

(see https://stackoverflow.com/questions/38346678/backup-and-restore-elasticsearch-elasticdump)