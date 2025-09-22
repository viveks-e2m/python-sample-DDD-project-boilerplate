import os
from sqlalchemy.ext.declarative import declarative_base
from fastapi import Depends
from sqlmodel import Field, Session, SQLModel, create_engine, select
from typing import Annotated
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database configuration - using SQLite instead of PostgreSQL
DATABASE_URL = "sqlite:///./test.db"

logger.info(f"Database URL: {DATABASE_URL}")

# SQLite-specific connect_args
connect_args = {"check_same_thread": False}

# Connection to database
engine = create_engine(DATABASE_URL, echo=True, connect_args=connect_args)


def create_db_and_tables():
    """
    Create database tables
    """
    try:
        SQLModel.metadata.create_all(engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")


def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]