import sqlite3
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Query, status
from pydantic import BaseModel, Field

DB_FILE = "tasks.db"

app = FastAPI(
    title="Task Management CRUD API (SQLite)",
    description="Extended Task API using SQLite for database persistence.",
    version="2.0.0",
)


# --- Schemas ---
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


# --- Database Helpers ---
def get_db_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row  # Enables dict-like access by column name
    return conn


def init_db():
    """Stage 0: Initialize database table and insert default tasks if empty."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Create table
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            done BOOLEAN NOT NULL CHECK (done IN (0, 1))
        )
    """
    )

    # Check if table is empty, insert initial example tasks
    cursor.execute("SELECT COUNT(*) FROM tasks")
    count = cursor.fetchone()[0]

    if count == 0:
        initial_tasks = [
            ("Buy groceries", False),
            ("Complete FastAPI assignment", True),
            ("Read SQLite documentation", False),
        ]
        cursor.executemany(
            "INSERT INTO tasks (title, done) VALUES (?, ?)", initial_tasks
        )
        conn.commit()

    conn.close()


# Run DB initialization on startup
@app.on_event("startup")
def startup_event():
    init_db()


# --- API Endpoints ---


@app.get("/tasks", response_model=List[TaskResponse])
def get_tasks(
    search: Optional[str] = Query(None, description="Search term in title"),
    done: Optional[bool] = Query(None, description="Filter by completion status"),
):
    """Stage 1 + Extras: Read all tasks with optional search & filter."""
    conn = get_db_connection()
    cursor = conn.cursor()

    query = "SELECT id, title, done FROM tasks WHERE 1=1"
    params = []

    if search:
        query += " AND title LIKE ?"
        params.append(f"%{search}%")

    if done is not None:
        query += " AND done = ?"
        params.append(1 if done else 0)

    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()

    return [
        {"id": row["id"], "title": row["title"], "done": bool(row["done"])}
        for row in rows
    ]


@app.get("/tasks/{task_id}", response_model=TaskResponse)
def get_task(task_id: int):
    """Stage 1: Read a single task by ID."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id, title, done FROM tasks WHERE id = ?", (task_id,)
    )
    row = cursor.fetchone()
    conn.close()

    if not row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
        )

    return {"id": row["id"], "title": row["title"], "done": bool(row["done"])}


@app.post(
    "/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED
)
def create_task(task: TaskCreate):
    """Stage 2: Insert a new task into the database."""
    if not task.title.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Title cannot be empty",
        )

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO tasks (title, done) VALUES (?, ?)",
        (task.title.strip(), 1 if task.done else 0),
    )
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()

    return {"id": new_id, "title": task.title.strip(), "done": task.done}


@app.put("/tasks/{task_id}", response_model=TaskResponse)
def update_task(task_id: int, task: TaskUpdate):
    """Stage 3: Update an existing task in the database."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Check existence
    cursor.execute("SELECT id, title, done FROM tasks WHERE id = ?", (task_id,))
    existing = cursor.fetchone()

    if not existing:
        conn.close()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
        )

    new_title = (
        task.title.strip()
        if task.title is not None
        else existing["title"]
    )
    new_done = (
        (1 if task.done else 0)
        if task.done is not None
        else existing["done"]
    )

    if task.title is not None and not new_title:
        conn.close()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Title cannot be empty",
        )

    cursor.execute(
        "UPDATE tasks SET title = ?, done = ? WHERE id = ?",
        (new_title, new_done, task_id),
    )
    conn.commit()
    conn.close()

    return {"id": task_id, "title": new_title, "done": bool(new_done)}


@app.delete("/tasks/{task_id}")
def delete_task(task_id: int):
    """Stage 3: Delete a task from the database."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM tasks WHERE id = ?", (task_id,))
    if not cursor.fetchone():
        conn.close()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
        )

    cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    conn.commit()
    conn.close()

    return {"message": f"Task {task_id} deleted successfully"}


@app.get("/stats")
def get_stats():
    """Optional Extra: Get statistics using SQL aggregate queries."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM tasks")
    total = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM tasks WHERE done = 1")
    completed = cursor.fetchone()[0]

    conn.close()

    return {
        "total_tasks": total,
        "completed_tasks": completed,
        "pending_tasks": total - completed,
    }