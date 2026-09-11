import os
import psycopg2
from psycopg2.extras import RealDictCursor
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Query, status
from pydantic import BaseModel, Field

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@db:5432/taskdb")

app = FastAPI(
    title="Task Management CRUD API (Postgres Docker)",
    description="Extended Task API using PostgreSQL database running in Docker.",
    version="3.0.0",
)

class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, description="Title of the task")
    done: bool = False

class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1)
    done: Optional[bool] = None

class TaskResponse(BaseModel):
    id: int
    title: str
    done: bool

def get_db_connection():
    conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
    return conn

@app.get("/tasks", response_model=List[TaskResponse])
def get_tasks(
    search: Optional[str] = Query(None, description="Search term in title"),
    done: Optional[bool] = Query(None, description="Filter by completion status"),
):
    conn = get_db_connection()
    cursor = conn.cursor()
    query = "SELECT id, title, done FROM tasks WHERE 1=1"
    params = []

    if search:
        query += " AND title ILIKE %s"
        params.append(f"%{search}%")
    if done is not None:
        query += " AND done = %s"
        params.append(done)

    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    return rows

@app.get("/tasks/{task_id}", response_model=TaskResponse)
def get_task(task_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, done FROM tasks WHERE id = %s", (task_id,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return row

@app.post("/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(task: TaskCreate):
    if not task.title.strip():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Title cannot be empty")
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO tasks (title, done) VALUES (%s, %s) RETURNING id, title, done",
        (task.title.strip(), task.done),
    )
    new_task = cursor.fetchone()
    conn.commit()
    conn.close()
    return new_task

@app.put("/tasks/{task_id}", response_model=TaskResponse)
def update_task(task_id: int, task: TaskUpdate):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, done FROM tasks WHERE id = %s", (task_id,))
    existing = cursor.fetchone()
    if not existing:
        conn.close()
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    new_title = task.title.strip() if task.title is not None else existing["title"]
    new_done = task.done if task.done is not None else existing["done"]

    cursor.execute(
        "UPDATE tasks SET title = %s, done = %s WHERE id = %s RETURNING id, title, done",
        (new_title, new_done, task_id),
    )
    updated_task = cursor.fetchone()
    conn.commit()
    conn.close()
    return updated_task

@app.delete("/tasks/{task_id}")
def delete_task(task_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM tasks WHERE id = %s", (task_id,))
    if not cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    cursor.execute("DELETE FROM tasks WHERE id = %s", (task_id,))
    conn.commit()
    conn.close()
    return {"message": f"Task {task_id} deleted successfully"}

@app.get("/stats")
def get_stats():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) as total FROM tasks")
    total = cursor.fetchone()["total"]
    cursor.execute("SELECT COUNT(*) as completed FROM tasks WHERE done = true")
    completed = cursor.fetchone()["completed"]
    conn.close()
    return {
        "total_tasks": total,
        "completed_tasks": completed,
        "pending_tasks": total - completed,
    }