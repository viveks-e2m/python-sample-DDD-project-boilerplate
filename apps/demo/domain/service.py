from datetime import datetime, timezone
from sqlmodel import select
from apps.demo.domain.models import DemoItem
from apps.demo.application.schemas import DemoCreateModel, DemoUpdateModel
from apps.demo.domain.exceptions import DemoItemNotFoundError, DemoItemPermissionError
from apps.demo.utils import audit_log
from database import Session


class DemoItemInstanceService:
    """
    Domain layer service class for demo item operations
    """
    
    def __init__(self, session: Session):
        self.session = session
    
    async def create_demo_item(self, demo_data: DemoCreateModel, current_user):
        """
        Domain layer service for creating a demo item
        
        Args:
            demo_data (DemoCreateModel): The data for the new demo item
            current_user: The user creating the item
            
        Returns:
            DemoItem: The created demo item
            
        Raises:
            DemoItemValidationError: If the demo data is invalid
        """
        demo_item = DemoItem(
            title=demo_data.title,
            description=demo_data.description,
            priority=demo_data.priority,
            created_by=current_user.username,
            created_at=datetime.now(timezone.utc),
            modified_at=datetime.now(timezone.utc)
        )
        self.session.add(demo_item)
        self.session.commit()
        self.session.refresh(demo_item)
        
        # Audit log
        audit_log("CREATE", current_user.username, demo_item.id, "Created new demo item")
        
        return demo_item
    
    async def get_demo_item(self, demo_id: int):
        """
        Domain layer service for retrieving a demo item
        
        Args:
            demo_id (int): The ID of the demo item to retrieve
            
        Returns:
            DemoItem: The requested demo item
            
        Raises:
            DemoItemNotFoundError: If the demo item is not found
        """
        statement = select(DemoItem).where(DemoItem.id == demo_id, DemoItem.is_active == True)
        demo_item = self.session.exec(statement).first()
        if not demo_item:
            raise DemoItemNotFoundError("Demo item not found")
        return demo_item
    
    async def update_demo_item(self, demo_id: int, demo_data: DemoUpdateModel, current_user):
        """
        Domain layer service for updating a demo item
        
        Args:
            demo_id (int): The ID of the demo item to update
            demo_data (DemoUpdateModel): The updated data for the demo item
            current_user: The user attempting to update the item
            
        Returns:
            DemoItem: The updated demo item
            
        Raises:
            DemoItemNotFoundError: If the demo item is not found
            DemoItemPermissionError: If the user lacks permission to update the item
        """
        statement = select(DemoItem).where(DemoItem.id == demo_id, DemoItem.is_active == True)
        demo_item = self.session.exec(statement).first()
        
        if not demo_item:
            raise DemoItemNotFoundError("Demo item not found")
            
        if demo_item.created_by != current_user.username and not current_user.is_superuser:
            raise DemoItemPermissionError("Not authorized to update this item")
            
        # Update only provided fields
        if demo_data.title is not None:
            demo_item.title = demo_data.title
        if demo_data.description is not None:
            demo_item.description = demo_data.description
        if demo_data.priority is not None:
            demo_item.priority = demo_data.priority
            
        demo_item.modified_at = datetime.now(timezone.utc)
        
        self.session.add(demo_item)
        self.session.commit()
        self.session.refresh(demo_item)
        
        # Audit log
        audit_log("UPDATE", current_user.username, demo_item.id, "Updated demo item")
        
        return demo_item
    
    async def delete_demo_item(self, demo_id: int, current_user):
        """
        Domain layer service for deleting a demo item (soft delete)
        
        Args:
            demo_id (int): The ID of the demo item to delete
            current_user: The user attempting to delete the item
            
        Returns:
            DemoItem: The deleted demo item
            
        Raises:
            DemoItemNotFoundError: If the demo item is not found
            DemoItemPermissionError: If the user lacks permission to delete the item
        """
        statement = select(DemoItem).where(DemoItem.id == demo_id)
        demo_item = self.session.exec(statement).first()
        
        if not demo_item:
            raise DemoItemNotFoundError("Demo item not found")
            
        if demo_item.created_by != current_user.username and not current_user.is_superuser:
            raise DemoItemPermissionError("Not authorized to delete this item")
            
        demo_item.is_active = False
        demo_item.modified_at = datetime.now(timezone.utc)
        
        self.session.add(demo_item)
        self.session.commit()
        self.session.refresh(demo_item)
        
        # Audit log
        audit_log("DELETE", current_user.username, demo_item.id, "Deleted demo item (soft delete)")
        
        return demo_item
    
    async def list_demo_items(self, current_user, skip: int = 0, limit: int = 100):
        """
        Domain layer service for listing demo items
        
        Args:
            current_user: The user requesting the list
            skip (int): Number of items to skip (for pagination)
            limit (int): Maximum number of items to return (for pagination)
            
        Returns:
            list[DemoItem]: List of demo items
        """
        statement = select(DemoItem).where(
            DemoItem.is_active == True
        ).offset(skip).limit(limit)
        
        demo_items = self.session.exec(statement).all()
        return demo_items