from auth import signup, login

user_id, msg = signup("chemuser1", "MySecurePass123")
print(msg, user_id)

user_id, msg = login("chemuser1", "MySecurePass123")
print(msg, user_id)

user_id, msg = login("chemuser1", "wrongpassword")
print(msg, user_id)