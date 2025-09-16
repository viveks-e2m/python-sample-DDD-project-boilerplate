import pytest
from sqlmodel import SQLModel
from database import engine


@pytest.fixture(scope="session")
def db_engine():
    """Database engine fixture"""
    return engine


@pytest.fixture(scope="function")
def db_session(db_engine):
    """Database session fixture"""
    # Create tables
    SQLModel.metadata.create_all(db_engine)
    
    # Create a new session
    from database import Session
    session = Session()
    
    yield session
    
    # Clean up after test
    session.close()
    SQLModel.metadata.drop_all(db_engine)