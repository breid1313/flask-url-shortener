import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
import json

from app.views.api.urls import get_url, post_url

"""
Exposes route to handle submissions from the index page 
"""


# define the Blueprint object
bp = Blueprint('submit', __name__, url_prefix='/')

def handle_submission(request):
    """Handler for requests to add a new record to the database.

    :param request: flask request
    :return: JSON response 
    :rtype: JSON
    """
    response = {}
    long_url = request.form["url"]
    if not long_url:
        # TODO validate URL format with regex
        error = "A URL is required in order to use the shortening portal."
        flash(error)
    else:
        response = post_url(long_url)
        response = json.loads(response.get_data())
    return response

def handle_redirect(request):
    """Handler for requests to get a record from the database
    and redirect to the original URL. If a record is not found,
    we re-render the index page with the response.

    :param request: flask request
    :return: a redirect or the index page
    """
    short_url = request.form["url"]
    if not short_url:
        error = "A URL is required in order to use the shortening portal."
        return

    response = get_url(short_url)
    response = json.loads(response.get_data())
    if response["response"] == 200:
        redirection = response["results"]["long_url"]
        # ensure the returned URL starts with http or https
        # otherwise flask with attemp to redirect to an internal URL
        if not (redirection.startswith("http://") or redirection.startswith("https://")):
            redirection = "https://" + redirection
        return redirect(redirection)
    else:
        return render_template('submit.html', response=response)

@bp.route("/submit", methods=["GET", "POST"])
@bp.route("/submit/", methods=["GET", "POST"])
def submit():
    """The /submit endpoint. Called when a user submits a request
    to add or get a record in the database. The request form's Submit
    field is named `shorten_url` in requests to add a record and
    `redirct_url` in requests to get a record so we can easily
    differentiate between the two.
    """
    error = None
    response = {}
    if request.method == "POST":
        if "shorten_url" in request.form:
            response = handle_submission(request)

        if "redirect_url" in request.form:
            return handle_redirect(request)

    return render_template('submit.html', response=response)