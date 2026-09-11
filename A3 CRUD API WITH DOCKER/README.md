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
<img width="1583" height="891" alt="image" src="https://github.com/user-attachments/assets/07bd0d63-80b3-4ead-91f6-195946b86e7d" />
<img width="1515" height="896" alt="image" src="https://github.com/user-attachments/assets/ac240dac-e92a-48dd-a01c-7a2b918ed9bc" />
<img width="736" height="449" alt="3" src="https://github.com/user-attachments/assets/7c593fa7-51a3-4629-961f-8c28ddec6ed3" />




Step 2: Stopping Containers (docker compose down)
The containers were stopped and removed to test persistence.
<img width="1361" height="546" alt="image" src="https://github.com/user-attachments/assets/43aff4a0-4aa1-4fed-bda1-689e4d055df7" />


Step 3: Restarting the Stack (docker compose up)
The stack was restarted using the persistent volume.
<img width="1350" height="480" alt="image" src="https://github.com/user-attachments/assets/dd82b983-df27-4cd7-bc37-f3f4de1a040c" />


Step 4: Data Verification (GET /tasks)
Calling the GET /tasks endpoint after restarting confirmed that all previously created tasks remained fully intact.
<img width="1123" height="778" alt="image" src="https://github.com/user-attachments/assets/61ca5187-70ca-484b-84ff-9b222ade61f8" />
<img width="1084" height="882" alt="image" src="https://github.com/user-attachments/assets/1925cb1e-babb-4fe0-8e1c-4b05b8f251a3" />



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
