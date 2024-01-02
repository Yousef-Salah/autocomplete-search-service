from functools import wraps

from elasticsearch import Elasticsearch
from flask import Flask, jsonify, render_template, request

app = Flask(__name__)

INDEX_NAME = "reuters"


def validate_autocomplete_endpoint_inputs(func):
    @wraps(func)
    def validate(*args, **kwargs):
        text: str = request.get_json()["text"]

        if type(text) == str and len(text.strip()) >= 3:
            return func(*args, *kwargs)
        else:
            return (
                jsonify(
                    message="Text argument must be string and at least consist of 3 characters"
                ),
                422,
            )

    return validate


def validate_query_endpoint_inputs(func):
    @wraps(func)
    def validate(*args, **kwargs):
        is_valid = True
        arguments = request.get_json()

        text: str = arguments["text"]
        longitude = arguments["longitude"]
        latitude = arguments["latitude"]

        if type(text) != str or len(text.strip()) < 3:
            is_valid = False

        # The latitude must be a number between -90 and 90
        # longitude between -180 and 180
        if type(latitude) == int or type(latitude) == float:
            latitude = float(latitude)
            if not (latitude <= 90) or not (latitude >= -90):
                is_valid = False
        else:
            is_valid = False

        if type(longitude) == int or type(longitude) == float:
            longitude = float(longitude)
            if not (longitude <= 180) or not (longitude >= -180):
                is_valid = False
        else:
            is_valid = False

        if is_valid:
            return func(*args, *kwargs)
        else:
            return (
                jsonify(
                    message="Text argument must be string and at least consist of 3 characters \n latitude must be a number between [-90, 90] and the longitude between [-180, 180]."
                ),
                422,
            )

    return validate


@app.route("/autocomplete", methods=["POST"])
@validate_autocomplete_endpoint_inputs
def autocomplete():
    print("OK", f"searcheed text is {request.get_json()}")
    params = request.get_json()
    text = params["text"]

    query = {
        "query": {"match": {"title": {"query": text, "analyzer": "text_processing"}}},
        "_source": ["title"],
    }

    response = es.search(index=INDEX_NAME, body=query)
    print(response)

    return jsonify(response["hits"]["hits"])


@app.route("/daily-distribution")
def daily_distribution():
    query = {
        "size": 0,
        "aggs": {
            "documents_over_time": {
                "date_histogram": {"field": "date", "calendar_interval": "1d"}
            }
        },
    }

    response = es.search(index=INDEX_NAME, body=query)

    return jsonify(response["aggregations"]["documents_over_time"])


@app.route("/query")
@validate_query_endpoint_inputs
def query():
    params = request.get_json()
    text = params["text"]
    longitude = params["longitude"]
    latitude = params["latitude"]
    query = {
        "query": {"multi_match": {"query": text, "fields": ["title^3", "body"]}},
        "sort": [
            {
                "_geo_distance": {
                    "location": {
                        "lat": latitude,
                        "lon": longitude,
                    },
                    "order": "asc",
                    "unit": "km",
                },
                "_geo_distance": {
                    "georeferences": {
                        "lat": latitude,
                        "lon": longitude,
                    },
                    "order": "asc",
                    "unit": "km",
                },
                "date": "desc",
            }
        ],
    }

    response = es.search(index=INDEX_NAME, body=query)

    return jsonify(response["hits"]["hits"])


@app.route("/top-10-georefernces")
def top_10_georeferences():
    query = {
        "size": 0,
        "aggs": {
            "top_georeferences": {
                "terms": {"field": "georeferences_string", "size": 10}
            }
        },
    }

    response = es.search(index=INDEX_NAME, body=query)

    return jsonify(response["aggregations"]["top_georeferences"]["buckets"])


@app.route("/home")
def home():
    return render_template("index.html")


if __name__ == "__main__":
    es = Elasticsearch("http://localhost:9200")
    app.run(debug=True, use_reloader=False)
