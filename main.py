from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import traceback

app = FastAPI(title="DebugX Demo Application")


# ============================================================
# DEMO USER DATA
# ============================================================

users = {
    "1": {
        "name": "Abhirami",
        "email": "user@example.com"
    }
}


# ============================================================
# HOME
# ============================================================

@app.get("/")
def home():
    return {
        "message": "DebugX Demo Application",
        "status": "running"
    }


# ============================================================
# USER ENDPOINT
# ============================================================

@app.get("/users/{user_id}")
def get_user(user_id: str):

    user = users.get(user_id)

    # INTENTIONAL BUG
    # /users/999 -> user becomes None
    # user["name"] -> TypeError

    return {
        "name": user["name"],
        "email": user["email"]
    }


# ============================================================
# DEBUGX INCIDENT CAPTURE
# ============================================================

@app.exception_handler(Exception)
async def debugx_exception_handler(
    request: Request,
    exc: Exception
):

    stack_trace = traceback.format_exc()

    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": "DebugX captured this incident.",

            "incident": {
                "method": request.method,
                "endpoint": request.url.path,
                "status_code": 500,
                "error_type": type(exc).__name__,
                "error_message": str(exc),
                "stack_trace": stack_trace,

                "source_code": """
@app.get("/users/{user_id}")
def get_user(user_id: str):

    user = users.get(user_id)

    return {
        "name": user["name"],
        "email": user["email"]
    }
"""
            }
        }
    )