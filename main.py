import os
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
from supabase import create_client, Client
from dotenv import load_dotenv

# Stage 0: Setup Supabase & Server
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

app = FastAPI(title="Auth Practice API")
security = HTTPBearer()

class UserCredentials(BaseModel):
    email: str = Field(min_length=1)
    password: str = Field(min_length=1)

# Stage 4: Middleware Guard
def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Extracts the Bearer token and verifies it with Supabase."""
    token = credentials.credentials
    try:
        # Stage 3: Token Verification
        response = supabase.auth.get_user(token)
        return response.user
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )

# Stage 1: Open Auth 
@app.post("/auth/signup", status_code=status.HTTP_201_CREATED)
def signup(creds: UserCredentials):
    try:
        response = supabase.auth.sign_up({
            "email": creds.email, 
            "password": creds.password
        })
        return response
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@app.post("/auth/login", status_code=status.HTTP_200_OK)
def login(creds: UserCredentials):
    try:
        response = supabase.auth.sign_in_with_password({
            "email": creds.email, 
            "password": creds.password
        })
        return {
            "access_token": response.session.access_token,
            "refresh_token": response.session.refresh_token
        }
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail=str(e)
        )

# Stage 4: Logout
@app.post("/auth/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(user=Depends(verify_token)):
    supabase.auth.sign_out()
    return None

# Stage 2: The Public & Protected Gates
@app.get("/public/info")
def get_public_info():
    return {"message": "Welcome stranger! This info is public."}

@app.get("/protected/profile")
def get_profile(user=Depends(verify_token)):
    return {
        "message": "Access granted.",
        "user_id": user.id,
        "email": user.email,
        "created_at": user.created_at
    }

@app.get("/protected/dashboard")
def get_dashboard(user=Depends(verify_token)):
    return {"message": "Welcome to your dashboard", "email": user.email}