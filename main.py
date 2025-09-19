from typing import AsyncGenerator
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from apps.user.interface import user_router, admin_router
from apps.user.interface.exception_handlers import http_exception_handler, validation_exception_handler
from contextlib import asynccontextmanager
from database import create_db_and_tables
from apps.user.application.schema import BaseResponse

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

# Custom exception handlers
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)

#Middlewares

# app.add_middleware(example_middleware)


app.include_router(user_router.router, prefix="/user" , tags=["User"])
app.include_router(admin_router.router, prefix="/user" , tags=["Admin"])
# app.include_router(auth_router.router, prefix="/auth" , tags=["Users"])
# app.include_router(post_router.router, prefix="/posts" , tags=["Posts"])
# app.include_router(admin_router.router, prefix="/custom_admin" , tags=["Custom Admin"])