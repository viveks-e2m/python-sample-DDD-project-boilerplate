# DDD Project Setup with Python and FastAPI

## Project Overview
This is a Python-based project using FastAPI, SQLAlchemy, and DDD (Domain-Driven Design) principles.

## Role-Based Access Control (RBAC)
This project now includes a comprehensive Role-Based Access Control system with:
- Role and Permission management
- Role-Permission assignment
- Service-based access control checking
- Dependency injection for route protection

### Database Models
The following models have been added to support RBAC:
- Role: Defines user roles (Admin, User, Moderator, etc.)
- Permission: Defines specific permissions (view_profile, manage_users, etc.)
- RolePermission: Junction table linking roles to permissions
- User: Extended with role_id foreign key

### Default Roles
- Admin: Full system access
- User: Basic user access
- Moderator: Content moderation privileges
- Maintainer: System maintenance privileges

### Default Permissions
- view_profile, edit_profile, delete_profile
- view_admin_dashboard
- manage_users, manage_roles
- view_maintainer_task

### Usage Example
```python
# In your route handlers:
from apps.user.interface.role_dependencies import require_permission

@router.get("/admin-dashboard")
def admin_dashboard(user=Depends(require_permission("view_admin_dashboard"))):
    return {"message": "Access granted to admin dashboard"}
```

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