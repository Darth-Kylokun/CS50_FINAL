from flask import Flask, session, render_template
from flask_session import Session

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")