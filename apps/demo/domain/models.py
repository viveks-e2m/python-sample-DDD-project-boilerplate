from apps.demo.application.schemas import DemoBase
from sqlmodel import Field, SQLModel
from datetime import datetime, timezone
from typing import Optional


#############################
##### Database model ########
#############################


class DemoItem(DemoBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_by: str = Field(
        foreign_key="users.username", index=True, nullable=False, ondelete="CASCADE"
    )
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    modified_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    is_active: bool = Field(default=True)
