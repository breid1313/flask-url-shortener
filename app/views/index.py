import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)

"""
Main index page of the flask webapp 
"""

# define the Blueprint 
bp = Blueprint('index', __name__, url_prefix='/')

# add the index routes
@bp.route("/", methods=["GET"])
@bp.route("/index", methods=["GET"])
@bp.route("/index/", methods=["GET"])
def index():
    return render_template('index.html')