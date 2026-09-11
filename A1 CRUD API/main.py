from fastapi import FastAPI, HTTPException

app = FastAPI(
    title="Task API",
    description="A simple task management API built with FastAPI",
    version="1.0"
)

# In-memory "database" pre-filled with 3 example tasks
tasks_db = [
    {"id": 1, "title": "Buy groceries", "done": False},
    {"id": 2, "title": "Complete Week 2 Assignment", "done": False},
    {"id": 3, "title": "Read FastAPI documentation", "done": True},
]

@app.get("/")
def read_root():
    return {"name": "Task API", "version": "1.0", "endpoints": ["/tasks"]}

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/tasks")
def get_all_tasks():
    return tasks_db

@app.get("/tasks/{task_id}")
def get_single_task(task_id: int):
    for task in tasks_db:
        if task["id"] == task_id:
            return task
    raise HTTPException(status_code=404, detail=f"Task {task_id} not found")      