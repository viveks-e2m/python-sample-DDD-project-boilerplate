import pytest
from sqlmodel import SQLModel, create_engine, Session
from sqlalchemy.pool import StaticPool


@pytest.fixture(name="session")
def session_fixture():
    """
    Create a test database session
    """
    engine = create_engine(
        "sqlite://",  # In-memory SQLite database for testing
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    
    # Create a new session
    session = Session(engine)
    
    yield session
    
    # Clean up after test
    session.close()
    SQLModel.metadata.drop_all(engine)