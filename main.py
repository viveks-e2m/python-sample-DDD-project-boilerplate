from typing import AsyncGenerator
from fastapi import FastAPI
from apps.user.interface import user_router
from contextlib import asynccontextmanager
from database import create_db_and_tables

"""
    This is the main entry point for the application.
"""

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    for loading resources that need to be present before the start of the application
    """
    # Events that will start before the application starts
    create_db_and_tables()
    # await create_default_superuser()
    yield
    # Events that will come after the application stops 


app = FastAPI(lifespan=lifespan)

#Middlewares

# app.add_middleware(example_middleware)


app.include_router(user_router.router, prefix="/user" , tags=["User"])
# app.include_router(auth_router.router, prefix="/auth" , tags=["Users"])
# app.include_router(post_router.router, prefix="/posts" , tags=["Posts"])
# app.include_router(admin_router.router, prefix="/custom_admin" , tags=["Custom Admin"])