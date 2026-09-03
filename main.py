from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel

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

    # Tell FastAPI what a new task looks like from the client
class TaskCreate(BaseModel):
    title: str

# --- Stage 3: Create Endpoint ---
@app.post("/tasks", status_code=status.HTTP_201_CREATED)
def create_task(task: TaskCreate):
    """Create a new task."""
    if task.title.strip() == "":
        raise HTTPException(status_code=400, detail="Title cannot be empty")
    
    new_id = max(t["id"] for t in tasks_db) + 1
    
    new_task = {
        "id": new_id, 
        "title": task.title, 
        "done": False
    }
    tasks_db.append(new_task)
    
    return new_task

    # Tell FastAPI what an update looks like (fields are optional)
class TaskUpdate(BaseModel):
    title: str | None = None
    done: bool | None = None

# --- Stage 4: Update Endpoint ---
@app.put("/tasks/{task_id}")
def update_task(task_id: int, updated_data: TaskUpdate):
    """Update an existing task by ID."""
    for task in tasks_db:
        if task["id"] == task_id:
            # Check if both title and done are missing/empty
            if updated_data.title is None and updated_data.done is None:
                raise HTTPException(status_code=400, detail="Provide at least a title or done status to update")
            
            if updated_data.title is not None:
                if updated_data.title.strip() == "":
                    raise HTTPException(status_code=400, detail="Title cannot be empty")
                task["title"] = updated_data.title
                
            if updated_data.done is not None:
                task["done"] = updated_data.done
                
            return task
            
    raise HTTPException(status_code=404, detail=f"Task {task_id} not found")

# --- Stage 4: Delete Endpoint ---
@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int):
    """Delete a task by ID."""
    for index, task in enumerate(tasks_db):
        if task["id"] == task_id:
            tasks_db.pop(index)
            return None # 204 No Content expects an empty response
            
    raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    
         