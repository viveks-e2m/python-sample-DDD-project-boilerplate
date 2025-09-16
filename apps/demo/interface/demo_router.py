from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from apps.demo.application.schemas import DemoCreateModel, DemoPublicModel, DemoUpdateModel, BaseResponse
from apps.demo.application.service import DemoItemApplicationService
from database import SessionDep
from typing import List, Optional

router = APIRouter()

@router.post("/", response_model=BaseResponse[DemoPublicModel], tags=["Demo"])
async def create_item(
    demo_data: DemoCreateModel,
    session: SessionDep,
    current_user: dict = Depends()  # Simplified for demo purposes
):
    """
    Create a new demo item.
    
    Creates a new demo item with the provided data. The item will be 
    associated with the currently authenticated user.
    
    Args:
        demo_data: The data for the new demo item
        session: Database session dependency
        current_user: Currently authenticated user
        
    Returns:
        BaseResponse containing the created demo item
        
    Raises:
        HTTPException: 400 - Invalid input data
        HTTPException: 401 - Authentication required
        HTTPException: 500 - Internal server error
    """
    try:
        service = DemoItemApplicationService(session)
        result = await service.create_demo_item(demo_data, current_user)
        return BaseResponse(success=True, data=result, message="Demo item created successfully")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred: {str(e)}"
        )

@router.get("/{demo_id}", response_model=BaseResponse[DemoPublicModel], tags=["Demo"])
async def read_item(
    demo_id: int = Path(..., ge=1, description="The ID of the demo item to retrieve"),
    session: SessionDep = Depends()
):
    """
    Get a demo item by ID.
    
    Retrieves a specific demo item by its unique identifier.
    
    Args:
        demo_id: The ID of the demo item to retrieve
        session: Database session dependency
        
    Returns:
        BaseResponse containing the requested demo item
        
    Raises:
        HTTPException: 404 - Demo item not found
        HTTPException: 500 - Internal server error
    """
    try:
        service = DemoItemApplicationService(session)
        result = await service.get_demo_item(demo_id)
        return BaseResponse(success=True, data=result, message="Demo item retrieved successfully")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred: {str(e)}"
        )

@router.put("/{demo_id}", response_model=BaseResponse[DemoPublicModel], tags=["Demo"])
async def update_item(
    demo_id: int = Path(..., ge=1, description="The ID of the demo item to update"),
    demo_data: Optional[DemoUpdateModel] = None,
    session: SessionDep = Depends(),
    current_user: dict = Depends()  # Simplified for demo purposes
):
    """
    Update a demo item.
    
    Updates an existing demo item with the provided data.
    
    Args:
        demo_id: The ID of the demo item to update
        demo_data: The updated data for the demo item
        session: Database session dependency
        current_user: Currently authenticated user
        
    Returns:
        BaseResponse containing the updated demo item
        
    Raises:
        HTTPException: 400 - Invalid input data
        HTTPException: 401 - Authentication required
        HTTPException: 403 - Insufficient permissions
        HTTPException: 404 - Demo item not found
        HTTPException: 500 - Internal server error
    """
    try:
        service = DemoItemApplicationService(session)
        result = await service.update_demo_item(demo_id, demo_data or DemoUpdateModel(), current_user)
        return BaseResponse(success=True, data=result, message="Demo item updated successfully")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred: {str(e)}"
        )

@router.delete("/{demo_id}", response_model=BaseResponse[DemoPublicModel], tags=["Demo"])
async def delete_item(
    demo_id: int = Path(..., ge=1, description="The ID of the demo item to delete"),
    session: SessionDep = Depends(),
    current_user: dict = Depends()  # Simplified for demo purposes
):
    """
    Delete a demo item (soft delete).
    
    Marks a demo item as inactive (soft delete) rather than removing it from the database.
    
    Args:
        demo_id: The ID of the demo item to delete
        session: Database session dependency
        current_user: Currently authenticated user
        
    Returns:
        BaseResponse containing the deleted demo item
        
    Raises:
        HTTPException: 401 - Authentication required
        HTTPException: 403 - Insufficient permissions
        HTTPException: 404 - Demo item not found
        HTTPException: 500 - Internal server error
    """
    try:
        service = DemoItemApplicationService(session)
        result = await service.delete_demo_item(demo_id, current_user)
        return BaseResponse(success=True, data=result, message="Demo item deleted successfully")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred: {str(e)}"
        )

@router.get("/", response_model=BaseResponse[List[DemoPublicModel]], tags=["Demo"])
async def list_items(
    session: SessionDep,
    current_user: dict = Depends(),  # Simplified for demo purposes
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of items to return")
):
    """
    List demo items.
    
    Retrieves a paginated list of active demo items.
    
    Args:
        session: Database session dependency
        current_user: Currently authenticated user
        skip: Number of items to skip (for pagination)
        limit: Maximum number of items to return (for pagination)
        
    Returns:
        BaseResponse containing a list of demo items
        
    Raises:
        HTTPException: 401 - Authentication required
        HTTPException: 500 - Internal server error
    """
    try:
        service = DemoItemApplicationService(session)
        result = await service.list_demo_items(current_user, skip, limit)
        return BaseResponse(success=True, data=result, message="Demo items retrieved successfully")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred: {str(e)}"
        )