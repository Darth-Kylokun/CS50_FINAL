from flask import Flask, session, render_template, request, _app_ctx_stack, flash, redirect
from flask_cors import CORS
from flask_session import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm.exc import NoResultFound
from tempfile import mkdtemp
from helpers import *
from models import *
from database import SessionLocal, Engine

Base.metadata.create_all(bind=Engine)

app = Flask(__name__)
CORS(app)
app.session = scoped_session(SessionLocal, scopefunc=_app_ctx_stack.__ident_func__)
app.config["TEMPLATES_AUTO_RELOAD"] = True

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
    username = app.session.query(User.username).filter(User.id == session["user_id"])
    return render_template("index.html", name=username)

@app.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        if not username:
            flash(u"Please Provide a Username", "danger")
            return render_template("register.html")
        email = request.form.get("email")
        if not email:
            flash(u"Please Provide a Email", "danger")
            return render_template("register.html")
        password = request.form.get("password")
        if not password:
            flash(u"Please Provide a Password", "danger")
            return render_template("register.html")
        if not validate_password(password):
            flash(u"Please Provide a Valid Password", "danger")
        password_confirm = request.form.get("password_confirm")
        if not password_confirm:
            flash(u"Please Confirm Your Password", "danger")
            return render_template("register.html")
        if password != password_confirm:
            flash(u"Make Sure Both of Your Passwords Match", "danger")
        session["user_id"] = 0

        key, salt = gen_hash_and_salt(password)
        new_user = User(username=username, email=email, hash=key, salt=salt)

        app.session.add(new_user)
        app.session.commit()
        user_id = app.session.query(User.id).one_or_none()

        session["user_id"] = user_id

        return redirect("/")
    else:
        return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        if not username:
            flash(u"Please Provide a Username", "danger")
            return render_template("register.html")
        password = request.form.get("password")
        if not password:
            flash(u"Please Provide a Password", "danger")
            return render_template("register.html")

        try:
            key, salt, user_id = app.session.query(User.hash, User.salt, User.id).filter(User.username == username).one()
        except NoResultFound:
            flash(u"Username not Recognized if you Haven't Registered Please Register", "danger")
            return render_template("register.html")

        if not verify_password(password, key, salt):
            flash(u"Incorrect Password", "danger")
            return render_template("register.html")

        session["user_id"] = user_id
        return redirect("/")
    else:
        return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

@app.teardown_appcontext
def remove_session(*args, **kwargs):
    app.session.remove()