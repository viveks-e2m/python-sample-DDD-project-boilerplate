import os
from sqlalchemy.ext.declarative import declarative_base
from fastapi import Depends
from sqlmodel import Field, Session, SQLModel, create_engine, select
from typing import Annotated, TypeAlias
import config
from apps.user.domain.models import User, PasswordResetToken
from apps.user.domain.auth_models import TwoFactorAuth, UserSession, OAuthAccount

# Database configuration
# Use PostgreSQL in production, SQLite for local development
if os.getenv("ENVIRONMENT") == "production":
    database_url = config.DATABASE_URL
else:
    # Default to SQLite for local development
    sqlite_file_name = "database.db"
    sqlite_url = f"sqlite:///./{sqlite_file_name}"
    database_url = os.getenv("DATABASE_URL", sqlite_url)

connect_args = {"check_same_thread": False} if database_url.startswith("sqlite") else {}

# Connection to database
engine = create_engine(database_url, connect_args=connect_args, echo=True)

def create_db_and_tables():
    """
    Create database tables
    """
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session
     
SessionDep = Annotated[Session, Depends(get_session)]