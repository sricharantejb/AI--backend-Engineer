from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from supabase import create_client
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

app = FastAPI(title="BE-03 Authentication API")


class User(BaseModel):
    email: str
    password: str


@app.get("/")
def home():
    return {"message": "Server running and connected to Supabase"}


# -----------------------------
# Signup
# -----------------------------
@app.post("/auth/signup", status_code=201)
def signup(user: User):

    if not user.email or not user.password:
        raise HTTPException(status_code=400,
                            detail="Email and Password required")

    try:
        response = supabase.auth.sign_up(
            {
                "email": user.email,
                "password": user.password
            }
        )

        return {
            "message": "User created successfully",
            "user": response.user
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# -----------------------------
# Login
# -----------------------------
@app.post("/auth/login")
def login(user: User):

    if not user.email or not user.password:
        raise HTTPException(status_code=400,
                            detail="Email and Password required")

    try:

        response = supabase.auth.sign_in_with_password(
            {
                "email": user.email,
                "password": user.password
            }
        )

        return {
            "access_token": response.session.access_token,
            "refresh_token": response.session.refresh_token,
            "token_type": "Bearer"
        }

    except Exception:

        raise HTTPException(
            status_code=401,
            detail="Invalid login credentials"
        )