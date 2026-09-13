# Secure Auth API

A robust FastAPI application demonstrating secure user authentication, JWT verification, and protected endpoint routing using Supabase.

## Setup Instructions

1. **Clone the repository**
2. **Set up the virtual environment:** `python -m venv venv`
3. **Install dependencies:** `pip install -r requirements.txt`
4. **Environment Variables:** Create a `.env` file at the root:
   SUPABASE_URL=your_project_url
   SUPABASE_KEY=your_anon_key
5. **Run the server:** `uvicorn main:app --reload`

## API Reference

| Endpoint | Method | Auth Required | Purpose |
|----------|--------|---------------|---------|
| `/auth/signup` | POST | No | Register a new user |
| `/auth/login` | POST | No | Authenticate & receive JWT |
| `/auth/logout` | POST | Yes | Terminate session |
| `/public/info` | GET | No | View public data |
| `/protected/profile` | GET | Yes | View protected user metadata |