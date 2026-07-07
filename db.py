import os
from dotenv import load_dotenv
from pymongo import MongoClient
from datetime import datetime

load_dotenv(dotenv_path="apis.env")

client = MongoClient(os.getenv("MONGODB_URI"))
db = client["labintel"]

users_collection = db["users"]
history_collection = db["chat_history"]


def create_user(username: str, hashed_password: str) -> str:
    """Create a new user. Returns user_id as string."""
    if users_collection.find_one({"username": username}):
        return None  # user already exists
    result = users_collection.insert_one({
        "username": username,
        "password": hashed_password,
        "created_at": datetime.utcnow()
    })
    return str(result.inserted_id)


def get_user(username: str):
    """Fetch a user by username."""
    return users_collection.find_one({"username": username})


def save_chat(user_id: str, query: str, response: str):
    """Save a query+response pair to chat history."""
    history_collection.insert_one({
        "user_id": user_id,
        "query": query,
        "response": response,
        "timestamp": datetime.utcnow()
    })


def get_chat_history(user_id: str, limit: int = 20):
    """Fetch recent chat history for a user, most recent first."""
    cursor = history_collection.find({"user_id": user_id}).sort("timestamp", -1).limit(limit)
    return list(cursor)