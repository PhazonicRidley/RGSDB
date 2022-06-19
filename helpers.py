# helper functions
from typing import Callable
from flask import redirect, session
from functools import wraps

ALLOWED_EXTENSIONS = {'zip', 'osz', 'osk', 'osr'}


def login_required(f: Callable) -> Callable:
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


def allowed_file(filename: str) -> bool:
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
