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

<img width="815" height="454" alt="8" src="https://github.com/user-attachments/assets/1c18362a-5120-4069-8651-79928c8a4552" />
<img width="810" height="430" alt="7" src="https://github.com/user-attachments/assets/1c8f8221-0ceb-44e3-89bb-51993a9cabb0" />
<img width="816" height="454" alt="6" src="https://github.com/user-attachments/assets/c15757d7-b918-43a1-95ae-5265c9f7e276" />
<img width="811" height="452" alt="5" src="https://github.com/user-attachments/assets/2f559d6a-ff1f-4343-858c-833dba3da025" />
<img width="836" height="451" alt="4" src="https://github.com/user-attachments/assets/91120fea-5a7d-4e87-bfe7-8776223f8bd7" />
<img width="815" height="439" alt="3" src="https://github.com/user-attachments/assets/a8f33b82-eff9-4f3a-a386-e77010094fbe" />
<img width="807" height="442" alt="2" src="https://github.com/user-attachments/assets/9a6841d7-d026-4bcd-9342-b759c85aedf3" />
<img width="872" height="440" alt="1" src="https://github.com/user-attachments/assets/8d6d549d-2e86-461b-911f-fa921968c021" />
