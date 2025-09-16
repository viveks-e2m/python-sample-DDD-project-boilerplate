# Demo App

This is a demonstration app that follows the Domain-Driven Design (DDD) architecture pattern used in this project.

## Structure

The app follows the same structure as other apps in the project:

```
demo/
├── domain/
│   ├── models.py          # Database models
│   └── service.py         # Domain logic and business rules
├── application/
│   ├── schemas.py         # Pydantic models for data validation
│   └── service.py         # Application layer services
├── interface/
│   └── demo_router.py     # API endpoints
├── Tests/
│   ├── conftest.py        # Test fixtures
│   └── test_demo_domain.py # Domain layer tests
├── dependency.py          # App-specific dependencies
└── __init__.py
```

## Components

### Domain Layer
- **models.py**: Contains the `DemoItem` database model
- **service.py**: Contains domain logic for demo items:
  - Creating demo items
  - Retrieving demo items
  - Updating demo items
  - Deleting demo items (soft delete)
  - Listing demo items

### Application Layer
- **schemas.py**: Contains Pydantic models for data validation:
  - `DemoBase`: Base model with common fields
  - `DemoPublicModel`: Model for public API responses
  - `DemoCreateModel`: Model for creating new items
  - `DemoUpdateModel`: Model for updating existing items
- **service.py**: Application services that orchestrate domain operations

### Interface Layer
- **demo_router.py**: FastAPI router with endpoints for:
  - Creating demo items (POST /)
  - Retrieving demo items (GET /{demo_id})
  - Updating demo items (PUT /{demo_id})
  - Deleting demo items (DELETE /{demo_id})
  - Listing demo items (GET /)

## Features

1. **CRUD Operations**: Full Create, Read, Update, Delete functionality
2. **Authentication**: All endpoints require authentication
3. **Authorization**: Users can only modify their own items (except superusers)
4. **Soft Delete**: Items are not permanently deleted, only marked as inactive
5. **Pagination**: List endpoint supports pagination

## Usage

To use this demo app in your project:

1. Register the router in your main application
2. Ensure database tables are created
3. The app will automatically integrate with the existing user authentication system

## Testing

The app includes unit tests for the domain layer services in the `Tests/` directory.