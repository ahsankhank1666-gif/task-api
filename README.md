# To-Do List CRUD API

A simple backend task management API built with FastAPI using in-memory storage.

## How to Run
1. Install dependencies:
   ```bash
   python -m pip install fastapi "uvicorn[standard]".
   
  1. Start the server:

Bash
python -m uvicorn main:app --reload

2.Open your browser at http://localhost:8000/docs to access Swagger UI.

Endpoints Table
Method,Endpoint,Description,Status Codes
GET,/,API Root info,200
GET,/health,Server health check,200
GET,/tasks,List all tasks,200
GET,/tasks/{id},Get a single task by ID,"200, 404"
POST,/tasks,Create a new task,"201, 400"
PUT,/tasks/{id},Update an existing task,"200, 400, 404"
DELETE,/tasks/{id},Remove a task,"204, 404"

Example curl -i Output
curl -i http://localhost:8000/health

Response:
HTTP/1.1 200 OK
date: Thu, 03 Sep 2026 12:00:00 GMT
server: uvicorn
content-length: 18
content-type: application/json

{"status":"ok"}

Swagger UI Screenshot:
<img width="1180" height="819" alt="image" src="https://github.com/user-attachments/assets/fbecac2c-2988-4264-949c-e1a2f308b967" />







