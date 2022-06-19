import os
import sys
from datetime import datetime
from tempfile import mkdtemp
from typing import Any, Optional, Union

import flask
from dotenv import load_dotenv
import psycopg
import psycopg_pool
from flask import (Flask, Response, redirect, render_template, request,
                   send_from_directory, session)
from flask_session import Session
from psycopg.rows import dict_row
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename

from helpers import allowed_file, login_required  # allowed file will be used eventually

app = Flask(__name__)

if not os.path.isdir("repository/"):
    os.mkdir("repository/")
UPLOAD_FOLDER = "repository/"
load_dotenv()


@app.route('/files/<filename>')
def files(filename):
    """Route to handle downloading"""
    return send_from_directory(app.root_path + '/repository/', filename)


# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# TODO: unhardcode rgsdb schema and switch user to 'rgsdb'
with psycopg.connect(os.environ.get("POSTGRES")) as conn:
    # really bad hack that will be in place until I reorganize the pool (plan for docker)
    with conn.cursor() as cur:
        cur.execute("CREATE SCHEMA IF NOT EXISTS rgsdb")


class DbPool(psycopg_pool.ConnectionPool):

    def getconn(self, timeout: Optional[float] = None) -> psycopg.Connection[Any]:
        conn = super().getconn(timeout)
        # configure
        conn.execute("SET search_path = rgsdb")
        conn.row_factory = dict_row
        return conn


db = DbPool(os.environ.get("POSTGRES"))
with db.connection() as conn:
    with open('schema.sql', 'r') as f:
        conn.execute(f.read())

print("DB configured.")


# webapp

@app.route("/login", methods=["GET", "POST"])
def login() -> str:
    """Log user in"""
    # Forget any user_id
    session.clear()
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return flask.abort()

        # Ensure password was submitted
        elif not request.form.get("password"):
            return flask.abort()

        # Query database for username
        with db.connection() as conn:
            rows = conn.execute("SELECT * FROM users WHERE username = %s", (request.form.get("username"),)).fetchall()

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]['password_hash'], request.form.get("password")):
            return render_template("login.html", invalid_login=True)

        # Remember which user has logged in
        session["user_id"] = rows[0]['id']

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register() -> str:
    """Register user"""
    if request.method == "POST":
        # get user account data (password checking is done in js)
        username = request.form.get("username")
        password_plaintext = request.form.get("password")
        password_hash = generate_password_hash(password_plaintext, "sha256")
        # check if username is taken
        with db.connection() as conn:
            usr_exist = conn.execute("SELECT username FROM users WHERE username = %s", (username,)).fetchone()

        if usr_exist:
            return render_template("register.html", error=True,
                                   message="Username has been taken, please choose something else!")

        with db.connection() as conn:
            conn.execute("INSERT INTO users (username, password_hash) VALUES (%s, %s)", (username, password_hash))
        return redirect("/login")

    else:
        return render_template("register.html")


@app.route("/")
@login_required
def index() -> str:
    """Landing page"""
    python_version = sys.version
    flask_version = flask.__version__
    with db.connection() as conn:
        user = conn.execute("SELECT username FROM users WHERE id = %s", (session['user_id'],)).fetchone()['username']
    return render_template('index.html', python_version=python_version, flask_version=flask_version, user=user)


@app.route("/logout")
@login_required
def logout() -> Response:
    """Handles logging out"""
    session.clear()
    return redirect("/")


@app.route("/repository")
@login_required
def repository():
    """Clone Hero song list"""
    with db.connection() as conn:
        clonehero = conn.execute("SELECT *, id::varchar FROM chsong").fetchall()
        osusongs = conn.execute("SELECT *, id::varchar FROM osusong").fetchall()
        osuskin = conn.execute("SELECT *, id::varchar FROM osuskin").fetchall()
        osureplay = conn.execute("SELECT *, id::varchar FROM osureplay").fetchall()
        for i in range(len(clonehero)):
            name = conn.execute("SELECT username FROM users WHERE id = %s", (data[i]['user_id'],)).fetchone()
            if name:
                clonehero[i]['username'] = name['username']

    return render_template("list.html", data_dict=clonehero)


@app.route("/repository/add", methods=['POST', 'GET'])
@login_required
def add_data() -> Union[str, Response]:
    """Add data"""
    if request.method == 'POST':
        id = str(int(datetime.now().timestamp() * 1e3 - datetime(2020, 12, 19).timestamp() * 1e3))
        data_type = request.form.get("datatype")
        name = request.form.get(f"{data_type}-name")
        artist = request.form.get(f"{data_type}-artist")
        skin_name = request.form.get(f"osuskin-name")
        player_name = request.form.get(f"osureplay-player")
        file = request.files["uploadedfile"]
        filename = request.files['uploadedfile'].filename
        fileext = filename[-3:]
        # TODO: handle this check in the frontend with javascript
        # sorry to anyone reading this code, I write bash scripts and this is just how my stuff works
        if name and file and allowed_file(file.filename):
            if data_type == "chsong" or data_type == "osusong":
                filename = secure_filename(id + " - " + artist + " - " + name)
            elif data_type == "osuskin":
                filename = secure_filename(id + " - " + skin_name)
            elif data_type == "osureplay":
                filename = secure_filename(id + " - " + player_name + " - " + name)
            filename = filename.replace("_", " ")
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename + "." + fileext))
            with db.connection() as conn:
                if data_type == "chsong":
                    conn.execute(
                        """
                    INSERT INTO chsong (id, user_id, name, artist)
                    VALUES (%s, %s, %s, %s)
                    """, (id, session['user_id'], name.strip(), artist,))
                elif data_type == "osusong":
                    conn.execute(
                        """
                    INSERT INTO osusong (id, user_id, name, artist, type)
                    VALUES (%s, %s, %s, %s)
                    """, (id, session['user_id'], name.strip(), artist,))
                elif data_type == "osuskin":
                    conn.execute(
                        """
                    INSERT INTO osuskin (id, user_id, skin_name)
                    VALUES (%s, %s, %s)
                    """, (id, session['user_id'], skin_name,))
                elif data_type == "osureplay":
                    conn.execute(
                        """
                    INSERT INTO osureplay (id, user_id, player, name)
                    VALUES (%s, %s, %s, %s)
                    """, (id, session['user_id'], player_name.strip(), name.strip(),))

        else:
            return render_template('add.html', error=True)
        return redirect("/repository")

    else:
        return render_template("add.html")


@app.route("/repository/delete", methods=['GET', 'POST'])
@login_required
def delete_data():
    """Removes Data"""
    if request.method == 'GET':
        with db.connection() as conn:
            user_added_data = conn.execute("SELECT * FROM data WHERE user_id = %s", (session['user_id'],)).fetchall()
        if user_added_data is None:
            return render_template("delete.html", error=True)

        return render_template('delete.html', user_data=user_added_data)
    else:  # POST
        entry_ids = request.form.keys()
        with db.connection() as conn:
            for entry_id in entry_ids:
                conn.execute("DELETE FROM data WHERE id = %s", (entry_id,))

        return render_template("delete.html", deletion_msg="Item deleted!")
