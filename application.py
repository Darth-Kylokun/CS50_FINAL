from flask import Flask, session, render_template, request
from flask_session import Session

app = Flask(__name__)

@app.route("/")
def index():
    # TODO
    return render_template("index.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        pass
    else:
        return render_template("register.html")