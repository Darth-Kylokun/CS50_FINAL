import hashlib
import os

def is_logged_in():
    pass

def hash_and_salt_password(password: str) -> tuple:
    salt = os.urandom(32)
    key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
    return (key, salt)

def verify_password(password_to_check: str, key: str, salt: str) -> bool:
    verify_key = hashlib.pbkdf2_hmac('sha256', password_to_check.encode('utf-8'), salt, 100000)
    if verify_key == key:
        return True
    return False