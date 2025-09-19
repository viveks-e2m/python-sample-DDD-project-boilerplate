from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from apps.user.application.schema import BaseResponse
from typing import Union, Any, Dict, List, Optional


# Custom exception handler for HTTPException
async def http_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    # Make sure it's an HTTPException
    if not isinstance(exc, HTTPException):
        # If it's not an HTTPException, re-raise it
        raise exc
        
    # Extract error details
    error_details: Dict[str, Any] = {
        "message": exc.detail,
        "status_code": exc.status_code
    }
    
    # Add headers if they exist
    if hasattr(exc, 'headers') and exc.headers:
        error_details["headers"] = exc.headers
    
    return JSONResponse(
        status_code=exc.status_code,
        content=BaseResponse(
            success=False,
            message=exc.detail,
            data=None,
            status_code=exc.status_code,
            error_details=error_details
        ).model_dump()
    )


# Custom exception handler for validation errors
async def validation_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    # Make sure it's a RequestValidationError
    if not isinstance(exc, RequestValidationError):
        # If it's not a RequestValidationError, re-raise it
        raise exc
    
    # Extract error details
    error_details: List[Dict[str, str]] = []
    for error in exc.errors():
        error_details.append({
            "field": ".".join(str(loc) for loc in error["loc"]),
            "message": error["msg"],
            "type": error["type"]
        })
    
    # Create a user-friendly error message
    error_message = "Validation failed"
    if error_details:
        error_message = error_details[0]["message"] if len(error_details) == 1 else "Multiple validation errors occurred"
    
    return JSONResponse(
        status_code=422,
        content=BaseResponse(
            success=False,
            message=error_message,
            data=None,
            status_code=422,
            error_details=error_details
        ).model_dump()
    )