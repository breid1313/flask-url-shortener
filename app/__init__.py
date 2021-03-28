#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from flask import Flask

"""
This file is the Flask "Application Factory" logic.
It contains all the necessary logic to load app configurations,
set the sqlite database, and expose the routes/views provided.
"""

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    #########
    # routes
    #########
    from . import db
    db.init_app(app)

    from .views import submit
    app.register_blueprint(submit.bp)

    from .views import index
    app.register_blueprint(index.bp)

    from .views.api import urls
    app.register_blueprint(urls.bp)
    #########
    # end routes
    #########

    return app