from flask import Flask, session, render_template, request, _app_ctx_stack, flash, redirect
from flask_cors import CORS
from flask_session import Session
from sqlalchemy import and_
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
    username = app.session.query(User.username).filter(User.id == session["user_id"]).one()[0]
    return render_template("index.html", name=username)

@app.route("/boards", methods=['GET', 'POST'])
@is_logged_in
def boards():
    if request.method == "POST":
        title = request.form.get("title_input")
        if not title:
            flash(u"Please Provide a Title For Your Board", "danger")
            return render_template("/boards.html")
        
        description = request.form.get("description_input")
        user_id = session["user_id"]

        board = Board(user_id=user_id, title=title, description=description)

        try:
            app.session.add(board)
            app.session.commit()            
        except:
            app.session.rollback()
            flash(u"You done goofed up now", "danger")
            return render_template("boards.html")
        
        board_id = app.session.query(Board.id).filter(and_(Board.user_id == session["user_id"], Board.title == title)).one()[0]
        return redirect(f"boards/{board_id}")
    else:
        boards = app.session.query(Board.id, Board.title, Board.description).filter(Board.user_id == session["user_id"]).all()
        return render_template("boards.html", boards=boards)

@app.route("/deleteOrOpenBoard", methods=["POST"])
@is_logged_in
def open_or_delete_board():
    board_id = request.form.get("board_to_open")
    if not board_id:
        board_id = request.form.get("board_to_close")
        board_to_delete = app.session.query(Board).filter(Board.id == int(board_id)).delete()
        app.session.commit()
        flash(u"Succesfully Deleted Board", "success")
        return redirect("/boards")
    
    return redirect(f"/boards/{board_id}")

@app.route("/addList/<int:board_id>", methods=["POST"])
@is_logged_in
def add_list(board_id):
    title = request.form.get("title_input")
    if not title:
        flash(u"Please Provide a Title", "danger")
        return redirect(f"boards/{board_id}")
    description = request.form.get("description_input")
    board_list = List(board_id=board_id, title=title, description=description)
    app.session.add(board_list)
    app.session.commit()
    return redirect(f"/boards/{board_id}")

@app.route("/editList/<int:board_id>", methods=["POST"])
@is_logged_in
def edit_list(board_id):
    title = request.form.get("title_edit")
    print(title)
    if not title:
        flash(u"Please Make Sure You Have a Title", "danger")
        return redirect(f"/board/{board_id}")
    description = request.form.get("description_edit")
    list_id = int(request.form.get("list_id"))

    app.session.query(List).filter(List.id == list_id).update({List.title: title, List.description: description}, synchronize_session = False)
    app.session.commit()

    return redirect(f"/boards/{board_id}")

@app.route("/boards/<int:board_id>")
@is_logged_in
def board(board_id):
    title = app.session.query(Board.title).filter(and_(Board.user_id == session["user_id"], Board.id == board_id)).one()[0]
    try:
        lists = app.session.query(List.id, List.title, List.description).filter(List.board_id == board_id, ).all()
    except ValueError:
        pass

    return render_template("board.html", title=title, lists=lists, board_id=board_id)

@app.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        if not username:
            flash(u"Please Provide a Username", "danger")
            return render_template("register.html")
        if not validate_username(username):
            flash(u"Please Provide a Valid Username")
            return render_template("register.html")

        email = request.form.get("email")
        if not email:
            flash(u"Please Provide a Email", "danger")
            return render_template("register.html")
        if not validate_email(email):
            flash(u"Please Provide a Valid Email")
            return render_template("register.html")

        password = request.form.get("password")
        if not password:
            flash(u"Please Provide a Password", "danger")
            return render_template("register.html")
        if not validate_password(password):
            flash(u"Please Provide a Valid Password", "danger")
            return render_template("register.html")

        password_confirm = request.form.get("password_confirm")
        if not password_confirm:
            flash(u"Please Confirm Your Password", "danger")
            return render_template("register.html")

        if password != password_confirm:
            flash(u"Make Sure Both of Your Passwords Match", "danger")
            return render_template("register.html")

        key, salt = gen_hash_and_salt(password)
        try:
            new_user = User(username=username, email=email, hash=key, salt=salt)
            app.session.add(new_user)
            app.session.commit()
        except IntegrityError:
            app.session.rollback()
            flash(u"Username/Email is already taken", "danger")
            return render_template("register.html")
        
        user_id = app.session.query(User.id).filter(User.username == username).one()[0]
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
            return render_template("login.html")

        if not verify_password(password, key, salt):
            flash(u"Incorrect Password", "danger")
            return render_template("login.html")

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