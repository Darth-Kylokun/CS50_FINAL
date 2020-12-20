from flask import Flask, session, render_template, request, _app_ctx_stack, flash, redirect
from flask_cors import CORS
from flask_session import Session
from sqlalchemy.orm import scoped_session
from tempfile import mkdtemp
from helpers import is_logged_in
from models import *
from database import SessionLocal, Engine

Base.metadata.create_all(bind=Engine)
app = Flask(__name__)
CORS(app)
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.session = scoped_session(SessionLocal, scopefunc=_app_ctx_stack.__ident_func__)

@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

@app.route("/")
@is_logged_in
def index():
    # TODO
    return render_template("index.html")

@app.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        if username is None:
            flash(u"Please provide a username", "danger")
            return render_template("register.html")
        email = request.form.get("email")
        if email is None:
            flash(u"Please provide a email", "danger")
            return render_template("register.html")
        session["user_id"] = 0
        return redirect("/")
    else:
        return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        return ""
    else:
        return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")