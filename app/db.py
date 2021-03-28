#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sqlite3

import click
from flask import current_app, g
from flask.cli import with_appcontext


def get_db():
    """Gets the sqlite database
    `g` is a special flask object that contains information
    specific to each request.

    :return: sqlite database object
    :rtype: sqlite database object
    """
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row

    return g.db


def close_db(e=None):
    """Close the connection to the sqlite database after a request is complete.

    :param e: an error, defaults to None
    :type e: str, optional
    """
    db = g.pop('db', None)

    if db is not None:
        db.close()


def init_db():
    """Initializes the database"""
    db = get_db()

    # execute the script defined in schema.sql
    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))


@click.command('init-db')
@with_appcontext
def init_db_command():
    """Register the init-db command to the flask cli as `flask init-db`"""
    init_db()
    click.echo('Initialized the database.')

# register the db init and close functions with the app
def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
