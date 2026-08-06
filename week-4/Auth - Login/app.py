from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from supabase import create_client
from dotenv import load_dotenv
import os

# -----------------------------
# Load Environment Variables
# -----------------------------

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

app = FastAPI(
    title="BE-03 Authentication API",
    description="Backend AI Engineering Week 4 Assignment",
    version="1.0.0"
)

# -----------------------------
# Swagger Authentication
# -----------------------------

security = HTTPBearer()

# -----------------------------
# User Model
# -----------------------------

class User(BaseModel):
    email: str
    password: str

# -----------------------------
# Home Route
# -----------------------------

@app.get("/")
def home():
    return {
        "message": "Server running and connected to Supabase"
    }

# -----------------------------
# Public Route
# -----------------------------

@app.get("/public/info")
def public_info():
    return {
        "message": "Welcome stranger! This info is public."
    }

# -----------------------------
# Signup
# -----------------------------

@app.post("/auth/signup", status_code=201)
def signup(user: User):

    if not user.email or not user.password:
        raise HTTPException(
            status_code=400,
            detail="Email and Password required"
        )

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

        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

# -----------------------------
# Login
# -----------------------------

@app.post("/auth/login")
def login(user: User):

    if not user.email or not user.password:
        raise HTTPException(
            status_code=400,
            detail="Email and Password required"
        )

    try:

        response = supabase.auth.sign_in_with_password(
            {
                "email": user.email,
                "password": user.password
            }
        )

        return {

            "message": "Login Successful",

            "access_token": response.session.access_token,

            "refresh_token": response.session.refresh_token,

            "token_type": "Bearer"

        }

    except Exception:

        raise HTTPException(
            status_code=401,
            detail="Invalid login credentials"
        )

# -----------------------------
# Verify Token
# -----------------------------

def verify_token(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):

    token = credentials.credentials

    try:

        user = supabase.auth.get_user(token)

        if user.user is None:
            raise HTTPException(
                status_code=401,
                detail="Invalid or Expired Token"
            )

        return user.user

    except Exception:

        raise HTTPException(
            status_code=401,
            detail="Invalid or Expired Token"
        )

# -----------------------------
# Protected Profile
# -----------------------------

@app.get("/protected/profile")
def profile(user=Depends(verify_token)):

    return {

        "id": user.id,

        "email": user.email,

        "created_at": user.created_at

    }

# -----------------------------
# Protected Dashboard
# -----------------------------

@app.get("/protected/dashboard")
def dashboard(user=Depends(verify_token)):

    return {

        "message": "Welcome to your Dashboard",

        "email": user.email

    }

# -----------------------------
# Logout
# -----------------------------

@app.post("/auth/logout", status_code=204)
def logout(user=Depends(verify_token)):

    try:

        supabase.auth.sign_out()

        return

    except Exception:

        raise HTTPException(
            status_code=400,
            detail="Logout Failed"
        )