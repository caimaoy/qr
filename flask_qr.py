#!/usr/bin/env python
# encoding: utf-8

import os
import sqlite3
import time
from flask import Flask, render_template, request, jsonify, g
from flask_debugtoolbar import DebugToolbarExtension

app = Flask(__name__)

app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'qr.db'),
    DEBUG=True,
    SECRET_KEY='development key',
))


@app.route('/test')
def hello_world():
    return 'Hello World!'


@app.route('/')
def input_qr():
    return render_template('qr.html')


@app.route('/qr_text_upload', methods=['POST'])
def upload_text():
    data = {'text': 'ret_' + request.form['text'], 'status': 0}
    t = request.form['text']
    if t:
        insert_text_into_db(t)
    return jsonify(data)


def insert_text_into_db(text):
    db = get_db()
    db.execute(
        'insert into t_qr_text (text, time) values (?, ?)',
        [text, int(time.time())]
    )
    db.commit()
    app.logger.debug('commit %s.' % text)


def connect_db():
    """Connects to the specific database"""
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv


def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db


def init_db():
    with app.app_context():
        db = get_db()
    with app.open_resource('qr.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()


@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()


toolbar = DebugToolbarExtension(app)

if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True)
