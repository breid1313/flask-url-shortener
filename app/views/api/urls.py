import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, jsonify
)
import json

from app.db import get_db

"""
Exposes the /api/urls endpoint as the REST API service.
This file also contains the logic to shorten URLs and read/write to the database.
"""

# Define the Blueprint object
bp = Blueprint('api', __name__, url_prefix='/api')

def get_last_id(db):
    """Gets the ID of the last record submitted to the database.

    :param db: sqlite database accessor as define in app/db.py get_db()
    :return: max value of the id column
    :rtype: int
    """
    row = db.execute("SELECT MAX(id) AS max_id FROM urls").fetchone()
    if not row[0]:
        # handle the case where the database is empty (sqlite indexes from 1)
        return 0
    max_id = int(row[0])
    return max_id

def int_to_hex(integer):
    """Converts a decimal (base 10 integer) to a hexadecimal (base 16)

    :param integer: a decimal integer
    :type integer: int
    :return: hexadecimal
    :rtype: str
    """
    conversion_table = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9",\
    "a", "b", "c", "d", "e", "f"]
    hexadecimal = ""

    # avoid an infinite loop if the input is 0
    if integer == 0:
        return "0"

    while(integer>0):
        remainder = integer%16
        hexadecimal = conversion_table[remainder]+ hexadecimal
        integer = integer//16
    return hexadecimal

def generate_short_url(index):
    """Generates a shortened url based an index integer.
    All urls have the format `cnjr.lnk/<hexadecimal>`
    We use hexadecimals to save characters when the database gets large.

    :param index: integer
    :type index: int
    :return: shortened url of the form `cnjr.lnk/<hexadecimal>`
    :rtype: str
    """
    base_url = "cnjr.lnk/"
    hex_hash = int_to_hex(index)
    return base_url + hex_hash


def post_url(long_url):
    """Adds a record to the database. We submit a long_url with its 
    generated short_url. The short url is based off the id of the record that
    we are going to submit in order to guaranntee uniqueness.

    :param long_url: A URL
    :type long_url: str
    :return: response to the request
    :rtype: JSON
    """
    db = get_db()
    error = None

    # if the long_url was not explicitly provided, the request
    # was made from outside the flask app
    if not long_url:
        data = json.loads(request.get_data())
        long_url = data["url"]

    # TODO validate URL

    # alert the user if they are submitting a duplicate URL
    if db.execute(
        "SELECT id FROM urls WHERE long_url = ?", (long_url,)
    ).fetchone() is not None:
        error = "A shortened URL for {0} has already been generated.".format(long_url)
        flash(error)

    else:
        last_id = get_last_id(db)
        # base the short url off the next index in the database
        short_url = generate_short_url(last_id + 1)
    
    if not error:
        # add the record
        db.execute(
            "INSERT INTO urls (long_url, short_url) VALUES (?, ?)",
            (long_url, short_url,)
        )
        db.commit()
        # respond 201 resource created with both URLs
        return jsonify({
            "response": 201,
            "content": {
                "long_url": long_url,
                "short_url": short_url
            }
        })
    # return the error to the requestor
    return jsonify({
        "response": 500,
        "error": error
    })

def get_url(short_url):
    """Gets a record from the database by a unique short_url
    generated from post_url()

    :param short_url: shortened URL of the form `cnjr.lnk/<hexadecimal`
    :type short_url: str
    :return: response to the request
    :rtype: JSON
    """
    db = get_db()
    error = None

    # if the short_url was not explicitly provided, the request
    # was made from outside the flask app
    if not short_url:
        data = json.loads(request.get_data())
        short_url = data["url"]

    # get the row from the database
    row = db.execute(
        "SELECT * FROM urls where short_url = ?", (short_url,)
    ).fetchone()

    if row:
        # format the json response
        # the database returns a Row object that mimics a tuple
        results = {
            "id": row[0],
            "long_url": row[1],
            "short_url": row[2]
        }
        return jsonify({"response": 200, "content": results})
    # if no row was found, return a 404
    return respond_404()
    

def respond_404():
    """Defines a universal 404 response for the API.

    :return: 404 response
    :rtype: JSON
    """
    return jsonify({"response": 404, "results": "Content not found."})


@bp.route("/urls", methods=["GET", "POST"])
@bp.route("/urls/", methods=["GET", "POST"])
def handle_request(long_url=None, short_url=None):
    """Handler for all requests to the /api/urls endpoint.

    :param long_url: a URL, defaults to None
    :type long_url: str, optional
    :param short_url: shortened URL of the form `cnjr.lnk/<hexadecimal`, defaults to None
    :type short_url: str, optional
    :return: response to the request
    :rtype: JSON
    """
    db = get_db()
    error = None

    if request.method == "POST":
        return post_url(long_url)
    if request.method == "GET":
        return get_url(short_url)
