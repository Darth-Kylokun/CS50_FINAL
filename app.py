from flask import Flask, session, render_template, request, _app_ctx_stack, flash, redirect, jsonify
from flask_cors import CORS
from flask_session import Session
from sqlalchemy import and_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm.exc import NoResultFound
from tempfile import mkdtemp
from helpers import is_logged_in, gen_hash_and_salt, verify_password, validate_email, validate_password, validate_username
from models import User, Board, List
from database import SessionLocal, Engine, Base
from werkzeug.exceptions import HTTPException

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

# TODO
# 1. Finish Up AJAX for boards.js
#    a. disable buttons once pressed
#    b. renable afterwards
#    c. hide modal after done
#    d. modify board button name after edit is done
# 2. Set maxlengths everywhere possible
# 3. Color theme it?
# 3. Other things(idk ¯\_(ツ)_/¯)

@app.route("/", methods=["GET", "POST"])
@is_logged_in
def index():
    if request.method == "POST":
        title = request.form.get("title_input")
        if not title:
            flash(u"Please Provide a Title For Your Board", "danger")
            return render_template("/boards.html")

        try:
            temp = app.session.query(Board).filter(and_(Board.user_id == session["user_id"], Board.title == title)).one()
            flash(u"Please Make Sure All Your Boards Have Unique Names", "danger")
            return render_template("boards.html")
        except:
            pass

        description = request.form.get("description_input")
        user_id = session["user_id"]

        board = Board(user_id=user_id, title=title, description=description)

        app.session.add(board)
        app.session.commit()

        board_id = app.session.query(Board.id).filter(and_(Board.user_id == session["user_id"], Board.title == title)).one()[0]
        return redirect(f"boards/{board_id}")
    else:
        boards = app.session.query(Board.id, Board.title, Board.description).filter(Board.user_id == session["user_id"]).all()
        username = app.session.query(User.username).filter(User.id == session["user_id"]).one()[0]
        return render_template("boards.html", boards=boards, username=username)

@app.route("/about")
@is_logged_in
def about():
    return render_template("about.html")

@app.route("/modListPos", methods=["POST"])
@is_logged_in
def mod_list_pos():
    data = request.get_json()
    list_id = int(data["list_id"])
    new_col_id = int(data["new_col_id"])
    
    app.session.query(List).filter(List.id == list_id).update({List.list_position: new_col_id})
    app.session.commit()

    return ""

@app.route("/deleteBoard", methods=["POST"])
@is_logged_in
def delete_board():
    board_id = request.get_json()["board_id"]
    app.session.query(Board).filter(Board.id == int(board_id)).delete()
    lists_to_delete = List.__table__.delete().where(List.board_id == int(board_id))
    app.session.execute(lists_to_delete)
    app.session.commit()
    # flash(u"Succesfully Deleted Board", "success")
    return jsonify({})

@app.route("/editBoard", methods=["POST"])
@is_logged_in
def edit_board():
    data = request.get_json()
    app.session.query(Board).filter(Board.id == int(data["board_id"])).update({Board.title: data["title"], Board.description: data["desc"]})
    app.session.commit()

    return jsonify(data)

@app.route("/addList/<int:board_id>", methods=["POST"])
@is_logged_in
def add_list(board_id):
    data = request.get_json()
    title = data["title"]
    description = data["description"]

    board_list = List(board_id=board_id, title=title, description=description, list_position=1)
    
    app.session.add(board_list)
    app.session.commit()

    return jsonify({"board_id": board_id, "list_id": board_list.id, "list_title": title, "list_desc": description})

@app.route("/modifyList/<int:board_id>", methods=["POST"])
@is_logged_in
def modify_list(board_id):
    data = request.get_json()
    list_id = data["list_id"]

    if not data["to_delete"]:
        title = data["title"]
        description = data["desc"]

        app.session.query(List).filter(List.id == list_id).update({List.title: title, List.description: description})
        app.session.commit()

        return jsonify({})
    else:
        app.session.query(List).filter(List.id == list_id).delete()
        app.session.commit()

        return jsonify({})

@app.route("/boards/<int:board_id>")
@is_logged_in
def board(board_id):
    
    title = app.session.query(Board.title).filter(and_(Board.user_id == session["user_id"], Board.id == board_id)).one()[0]
    try:
        list_one = app.session.query(List.id, List.title, List.description).filter(and_(List.board_id == board_id, List.list_position == 1)).all()
    except ValueError:
        pass

    try:
        list_two = app.session.query(List.id, List.title, List.description).filter(and_(List.board_id == board_id, List.list_position == 2)).all()
    except ValueError:
        pass

    try:
        list_three = app.session.query(List.id, List.title, List.description).filter(and_(List.board_id == board_id, List.list_position == 3)).all()
    except ValueError:
        pass
    print("redirect")
    return render_template("board.html", title=title, list_one=list_one, list_two=list_two, list_three=list_three, board_id=board_id)

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
            flash(u"Username/Email is Already Taken", "danger")
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
            return render_template("login.html")
        password = request.form.get("password")
        if not password:
            flash(u"Please Provide a Password", "danger")
            return render_template("login.html")

        try:
            key, salt, user_id = app.session.query(User.hash, User.salt, User.id).filter(User.username == username).one()
        except NoResultFound:
            flash(u"Username Not Recognized", "danger")
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

@app.errorhandler(HTTPException)
def handle_exception(e):
    flash(f"{e.name}: {e.code}\n{e.description}", "danger")
    return redirect("/")

@app.teardown_appcontext
def remove_session(*args, **kwargs):
    app.session.remove()