
@app.get("/users/{user_id}")
def get_user(user_id: str):

    user = users.get(user_id)

    if user is None:
        return {
            "error": "User not found"
        }

    return {
        "name": user["name"],
        "email": user["email"]
    }
