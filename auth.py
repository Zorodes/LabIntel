import bcrypt
from db import create_user, get_user


def hash_password(plain_password: str) -> str:
    hashed = bcrypt.hashpw(plain_password.encode("utf-8"), bcrypt.gensalt())
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))


def signup(username: str, plain_password: str):
    hashed = hash_password(plain_password)
    user_id = create_user(username, hashed)
    if user_id is None:
        return None, "Username already exists"
    return user_id, "Signup successful"


def login(username: str, plain_password: str):
    user = get_user(username)
    if user is None:
        return None, "User not found"
    if verify_password(plain_password, user["password"]):
        return str(user["_id"]), "Login successful"
    return None, "Incorrect password"