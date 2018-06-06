from flask import Flask, request
import json

import scrapers

scrapertasks = ['get','sideload']

app = Flask(__name__)

def _contains(obj):
    return [element for element in dir(obj) if '__' not in element]

@app.route('/scrapers/<scraper>/<task>', methods=['GET','POST'])
def scrapers(scraper=False, task=False):
    
    if task and task not in scrapertasks:
        return json.dump({'404':'unsupported scraper task, should be {scrapertasks}'.format(**locals())})
    
    if not scraper:
        return json.dump({'Results': { 'Available scrapers' : _contains(scrapers) }})

    if not task:
        task = '__doc__'

    if scraper and task:
        return getattr(getattr(scrapers,scraper),task)(request.data)

@app.route('/')
def home():
    return json.dump({'Results':'This is the general endpoint of the INCA API'})
    
if __name__ == '__main__':
    app.run(debug=True)
                         
