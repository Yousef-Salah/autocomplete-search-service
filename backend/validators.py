from functools import wraps

from flask import jsonify, request


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
