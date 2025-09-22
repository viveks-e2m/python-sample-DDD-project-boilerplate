# DDD Project Setup with Python and FastAPI

## Project Overview
This is a Python-based project using FastAPI, SQLAlchemy, and DDD (Domain-Driven Design) principles.

## Alembic commands 
- alembic init alembic
for creating migration script
- alembic revision -m "create tgables" 
running migrations
- alembic upgrade head

## FastAPI commands 
starting development server
- fastapi dev main.py

starting uvicorn server manually
- uvicorn main:app --reload

## Docker Setup

### Prerequisites
- Docker
- Docker Compose

### Running with Docker
1. Copy the environment file:
   ```bash
   cp .env.example .env
   ```
   Then modify the values in `.env` as needed.

2. Build and run the services:
   ```bash
   docker-compose up --build
   ```

3. The application will be available at `http://localhost:8000`

### Running only the database with Docker
If you want to run only the database with Docker and the application locally:

1. Start the database:
   ```bash
   docker-compose up db
   ```

2. Run the application locally:
   ```bash
   uvicorn main:app --reload
   ```

### Stopping the services
```bash
docker-compose down
```

To stop and remove volumes (including database data):
```bash
docker-compose down -v
```