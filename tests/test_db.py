from db import create_user, get_user, save_chat, get_chat_history

# Test user creation
user_id = create_user("testuser", "fakehash123")
print("Created user_id:", user_id)

# Test fetch
user = get_user("testuser")
print("Fetched user:", user)

# Test chat save
if user_id:
    save_chat(user_id, "What is a CSTR?", "A CSTR is a Continuous Stirred Tank Reactor.")
    history = get_chat_history(user_id)
    print("Chat history:", history) 