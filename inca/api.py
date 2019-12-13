from flask import Flask, request
import json
import os
import scrapers

endpoints = dict(scrapers=scrapers)

app = Flask(__name__)


def _contains(obj):
    return [element for element in dir(obj) if "__" not in element]


@app.route("/<category>")
def show_options(category):
    result = endpoints.get(category, False)
    if not result:
        return json.dumps(
            {
                "Results": "INCA currently provides these endpoints: %s"
                % ", ".join(endpoints.keys())
            }
        )
    else:
        tasks = [
            task[:-3]
            for task in os.listdir(category)
            if category[:-1] in task and task[-3:] == ".py"
        ]
        return json.dumps(
            {"Results": "{category} provides these tasks: {tasks}".format(**locals())}
        )


@app.route("/<category>/<task>")
def run_task(category, task):
    data = request.data
    return " ACK, NOT IMPLEMENTED YET"


@app.route("/")
def home():
    return json.dumps({"Results": "This is the general endpoint of the INCA API"})


if __name__ == "__main__":
    app.run(debug=True)
