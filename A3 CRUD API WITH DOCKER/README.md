# FastAPI Task Management API with PostgreSQL & Docker Compose

A containerized RESTful CRUD API built using **FastAPI**, **PostgreSQL**, and **Docker Compose**. Designed following the **Repository Pattern** to ensure clean separation of concerns and database independence. Developed for Assignment 3 (Backend AI Engineering Internship).

---

## 🏗️ Tech Stack & Architecture

- **Framework:** FastAPI (Python 3.10+)
- **Database:** PostgreSQL (Relational Database)
- **Data Access:** Repository Pattern (SQLAlchemy / SQLModel / Asyncpg)
- **Containerization:** Docker & Docker Compose
- **Documentation:** Interactive Swagger UI (`/docs`)

---

## 🚀 Quick Start Guide

### Prerequisites
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed and running on your system.
- Git

### Running the Application Stack

1. **Clone the Repository:**
   ```bash
   git clone [https://github.com/ahsankhank1666-gif/task-api.git](https://github.com/ahsankhank1666-gif/task-api.git)
   cd task-api

   Environment Configuration:
Ensure the .env file is present in the root directory (refer to .env.example).

1:Build and Run with Docker Compose:

Bash
docker compose up --build

2:Access the API Documentation:

Open your browser and navigate to:
http://localhost:8000/docs

3:💾 Data Persistence Proof Test

The PostgreSQL database container is configured with a persistent named volume (postgres_data). Below is the step-by-step verification demonstrating that data persists across container shutdowns and re-creations.

Step 1: Creating Tasks (POST /tasks)
Tasks were created via the Swagger UI endpoint.

Step 2: Stopping Containers (docker compose down)
The containers were stopped and removed to test persistence.

Step 3: Restarting the Stack (docker compose up)
The stack was restarted using the persistent volume.

Step 4: Data Verification (GET /tasks)
Calling the GET /tasks endpoint after restarting confirmed that all previously created tasks remained fully intact.

📁 Project Structure
Plaintext
.
├── docs/                   # Persistence proof screenshots (1.png - 7.png)
├── .env                    # Active environment configuration
├── .env.example            # Environment template
├── Dockerfile              # Container configuration for FastAPI
├── docker-compose.yml      # Multi-container orchestration (Web + Postgres)
├── init.sql                # Database initialization script
├── main.py                 # Application entry point
├── README.md               # Documentation
└── requirements.txt        # Python dependencies