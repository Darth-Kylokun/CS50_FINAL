import hashlib
import os
import re
from functools import wraps
from flask import session, redirect

def is_logged_in(f):
    '''
    Decorate routes to require login.

    http://flask.pocoo.org/docs/1.0/patterns/viewdecorators/
    '''
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

def gen_hash_and_salt(password: str) -> tuple:
    salt = os.urandom(32)
    key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
    return (key, salt)

def verify_password(password_to_check: str, key: str, salt: str) -> bool:
    verify_key = hashlib.pbkdf2_hmac('sha256', password_to_check.encode('utf-8'), salt, 100000)
    if verify_key == key:
        return True
    return False

def validate_email(email: str) -> bool:
    if re.fullmatch(r'^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$', email):
        return True
    return False

def validate_password(password: str) -> bool:
    if re.fullmatch(r'[A-Za-z0-9@#$%^&+=]{8,}', password):
        return True
    return False

def validate_username(username: str) -> bool:
    if re.fullmatch(r"^(?=.{8,20}$)(?![_.])(?!.*[_.]{2})[a-zA-Z0-9._]+(?<![_.])$", username):
        return True
    return False