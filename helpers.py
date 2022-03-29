# helper functions
from flask import redirect, render_template, request, session
from functools import wraps
import sqlite3

ALLOWED_EXTENSIONS = {'zip', 'osz', 'osk', 'osr'}

def login_required(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/1.0/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

def dict_factory(cursor: sqlite3.Cursor, row: tuple) -> dict:
    """Converts a row tuple to dict"""
    if not row:
        return {}
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS