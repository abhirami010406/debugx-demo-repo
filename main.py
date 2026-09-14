from fastapi import FastAPI, HTTPException

app = FastAPI()

@app.get("/users/{user_id}")
def get_user(user_id: int):
    # Your user lookup logic here
    user = None  # or fetch from database
    
    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )
    
    return user
