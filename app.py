import flask
from flask import Flask, Response, render_template, request, session, redirect
from flask_session import Session
from tempfile import mkdtemp
import sys
import os
from werkzeug.utils import secure_filename
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import login_required, allowed_file
from datetime import datetime
import psycopg
import psycopg_pool
from psycopg.rows import dict_row


app = Flask(__name__)
if not os.path.isdir("songs/"):
        os.mkdir("songs/")
UPLOAD_FOLDER = "songs/"
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

# TODO: unhard code rgsdb schema and switch user to 'rgsdb'
with psycopg.connect("postgres://phazonic@localhost") as conn:
    # really bad hack that will be in place until I reorganize the pool (plan for docker)
    with conn.cursor() as cur:
        cur.execute("CREATE SCHEMA IF NOT EXISTS rgsdb")
class DbPool(psycopg_pool.ConnectionPool):
    def configure(self, conn: psycopg.Connection):
        conn.execute("SET search_path = rgsdb") # hardcoded because lazy
        conn.row_factory = dict_row

db = DbPool("postgres://phazonic@localhost")
with db.connection() as conn:
    with open('psql_schema.sql', 'r') as f:
        t = f.read()
        conn.execute(t)

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
            rows = conn.execute("SELECT * FROM users WHERE username = %s", (request.form.get("username"))).fetchall()

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]['password'], request.form.get("password")):
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
            db.execute("SELECT username FROM users WHERE username = %s", (username)).fetchone()
        if usr_exist:
            return render_template("register.html", error=True, message="Username has been taken, please choose something else!")

        db.execute("INSERT INTO users (username, password) VALUES (:username, :password)", {'username':username, 'password':password_hash})
        db.commit()
        return redirect("/login")

    else:
        return render_template("register.html")



@app.route("/")
@login_required
def index() -> str:
    """Landing page"""
    python_version = sys.version
    flask_version = flask.__version__
    user = db.execute("SELECT username FROM users WHERE id = :uid", {'uid':session['user_id']}).fetchone()['username']
    return render_template('index.html', python_version=python_version, flask_version=flask_version, user=user)


@app.route("/logout")
@login_required
def logout() -> Response:
    """Handles logging out"""
    session.clear()
    return redirect("/")

@app.route("/songs")
@login_required
def songs():
    """Clone Hero song list"""
    song_dict = db.execute("SELECT * FROM ch_songs")
    return render_template("songs.html", song_data=song_dict)

@app.route("/songs/add", methods=['POST', 'GET'])
@login_required
def add_song():
    """Add a song"""
    if request.method == 'POST':
        name = request.form.get("name")
        artist = request.form.get("artist")
        creation = request.form.get("creation")
        uploaded = str(datetime.now())
        file = request.files["uploadedfile"]
        # file nonsense here
        if file and allowed_file(file.filename):
            filename = secure_filename(artist + " - " + name)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename + ".zip"))
            print("File uploaded")
            db.execute(
                """
                INSERT INTO ch_songs (user_id, song_name, artist, song_creation, uploaded)
                VALUES (:uid, :name, :artist, :creation, :uploaded)
                """, {'uid':session['user_id'],'name':name, 'artist':artist, 'creation':creation, 'uploaded':uploaded})
            db.commit()
        return redirect("/songs")
    
    else:
        return render_template("add.html")

