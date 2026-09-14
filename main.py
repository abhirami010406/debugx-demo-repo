from fastapi import FastAPI, HTTPException

app = FastAPI()

users = {
    1: {
        "name": "Alice",
        "email": "alice@example.com"
    }
}

@app.get("/users/{user_id}")
def get_user(user_id: int):
    user = users.get(user_id)
    
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
        "name": user["name"],
        "email": user["email"]
    }