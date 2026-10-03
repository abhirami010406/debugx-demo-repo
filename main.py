from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException

from debugx_middleware import DebugXMiddleware


load_dotenv()


app = FastAPI()


app.add_middleware(
    DebugXMiddleware,
)


@app.get("/users/{user_id}")
def get_user(user_id: int):
    if user_id != 1:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    user = {
        "name": "Alice"
    }

    # Intentional error for DebugX testing
    return user.get('email')