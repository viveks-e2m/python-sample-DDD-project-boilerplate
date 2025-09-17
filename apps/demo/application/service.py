from typing import Any, Optional
from fastapi import Depends, HTTPException, status
from sqlmodel import select
from apps.demo.domain.models import DemoItem
from apps.demo.domain.service import DemoItemInstanceService
from apps.demo.domain.exceptions import DemoItemNotFoundError, DemoItemPermissionError
from apps.demo.application.schemas import DemoCreateModel, DemoUpdateModel
from apps.demo.utils import validate_demo_priority
from database import SessionDep

class DemoItemApplicationService:
    """
    Application layer service class for demo item operations
    """

    def __init__(self, session: SessionDep):
        self.session: SessionDep = session
        self.domain_service: DemoItemInstanceService = DemoItemInstanceService(session)

    async def create_demo_item(
        self,
        demo_data: DemoCreateModel,
        current_user: Users = Depends(get_current_user),
    ) -> DemoItem:
        """
        Application layer service for creating a demo item

        Args:
            demo_data (DemoCreateModel): The data for the new demo item
            current_user (Users): The user creating the item

        Returns:
            DemoItem: The created demo item

        Raises:
            HTTPException: 400 - Invalid input data
            HTTPException: 401 - Authentication required
        """
        # Validate priority
        if not validate_demo_priority(demo_data.priority):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Priority must be between 0 and 10",
            )

        try:
            return await self.domain_service.create_demo_item(demo_data, current_user)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create demo item: {str(e)}",
            )

    async def get_demo_item(self, demo_id: int):
        """
        Application layer service for retrieving a demo item

        Args:
            demo_id (int): The ID of the demo item to retrieve

        Returns:
            DemoItem: The requested demo item

        Raises:
            HTTPException: 404 - Demo item not found
        """
        try:
            return await self.domain_service.get_demo_item(demo_id)
        except DemoItemNotFoundError:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Demo item not found"
            )

    async def update_demo_item(
        self,
        demo_id: int,
        demo_data: DemoUpdateModel,
        current_user: Users = Depends(get_current_user),
    ):
        """
        Application layer service for updating a demo item

        Args:
            demo_id (int): The ID of the demo item to update
            demo_data (DemoUpdateModel): The updated data for the demo item
            current_user (Users): The user attempting to update the item

        Returns:
            DemoItem: The updated demo item

        Raises:
            HTTPException: 400 - Invalid input data
            HTTPException: 401 - Authentication required
            HTTPException: 403 - Insufficient permissions
            HTTPException: 404 - Demo item not found
        """
        # Validate priority if provided
        if demo_data.priority is not None and not validate_demo_priority(
            demo_data.priority
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Priority must be between 0 and 10",
            )

        try:
            return await self.domain_service.update_demo_item(
                demo_id, demo_data, current_user
            )
        except DemoItemNotFoundError:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Demo item not found"
            )
        except DemoItemPermissionError:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to update this item",
            )

    async def delete_demo_item(
        self, demo_id: int, current_user: Users = Depends(get_current_user)
    ):
        """
        Application layer service for deleting a demo item

        Args:
            demo_id (int): The ID of the demo item to delete
            current_user (Users): The user attempting to delete the item

        Returns:
            DemoItem: The deleted demo item

        Raises:
            HTTPException: 401 - Authentication required
            HTTPException: 403 - Insufficient permissions
            HTTPException: 404 - Demo item not found
        """
        try:
            return await self.domain_service.delete_demo_item(demo_id, current_user)
        except DemoItemNotFoundError:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Demo item not found"
            )
        except DemoItemPermissionError:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to delete this item",
            )

    async def list_demo_items(
        self,
        current_user: Users = Depends(get_current_user),
        skip: int = 0,
        limit: int = 100,
    ):
        """
        Application layer service for listing demo items

        Args:
            current_user (Users): The user requesting the list
            skip (int): Number of items to skip (for pagination)
            limit (int): Maximum number of items to return (for pagination)

        Returns:
            list[DemoItem]: List of demo items

        Raises:
            HTTPException: 401 - Authentication required
        """
        # Validate pagination parameters
        if skip < 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Skip must be greater than or equal to 0",
            )

        if limit < 1 or limit > 1000:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Limit must be between 1 and 1000",
            )

        try:
            return await self.domain_service.list_demo_items(current_user, skip, limit)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to list demo items: {str(e)}",
            )
