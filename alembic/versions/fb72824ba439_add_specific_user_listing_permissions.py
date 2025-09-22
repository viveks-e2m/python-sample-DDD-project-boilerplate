"""add_specific_user_listing_permissions

Revision ID: fb72824ba439
Revises: dce552376960
Create Date: 2025-09-22 18:30:53.325003

"""
from typing import Sequence, Union
import uuid
from datetime import datetime, timezone

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'fb72824ba439'
down_revision: Union[str, None] = 'dce552376960'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add specific user listing permissions
    connection = op.get_bind()
    now = datetime.now(timezone.utc)
    
    # Check if permissions already exist
    result = connection.execute(sa.text("SELECT COUNT(*) FROM permission WHERE name = 'list_all_users_admin'")).fetchone()
    if result is not None and result[0] == 0:
        # Insert specific permissions
        admin_perm_id = str(uuid.uuid4())
        maintainer_perm_id = str(uuid.uuid4())
        user_perm_id = str(uuid.uuid4())
        
        connection.execute(
            sa.text("""
                INSERT INTO permission (id, name, description, created_at, updated_at) 
                VALUES (:admin_perm_id, 'list_all_users_admin', 'Permission to list all users as admin', :now, :now),
                       (:maintainer_perm_id, 'list_all_users_role_maintainer', 'Permission to list users with maintainer role', :now, :now),
                       (:user_perm_id, 'list_all_users_role_user', 'Permission to list users with user role', :now, :now)
            """),
            {
                "admin_perm_id": admin_perm_id,
                "maintainer_perm_id": maintainer_perm_id,
                "user_perm_id": user_perm_id,
                "now": now
            }
        )
        
        # Assign permissions to roles
        # Get role IDs
        admin_role_result = connection.execute(sa.text("SELECT id FROM role WHERE name = 'Admin'")).fetchone()
        maintainer_role_result = connection.execute(sa.text("SELECT id FROM role WHERE name = 'Maintainer'")).fetchone()
        user_role_result = connection.execute(sa.text("SELECT id FROM role WHERE name = 'User'")).fetchone()
        
        if admin_role_result:
            admin_role_id = admin_role_result[0]
            # Admin gets all permissions
            connection.execute(
                sa.text("""
                    INSERT INTO rolepermission (id, role_id, permission_id, created_at) 
                    VALUES (:rp1_id, :admin_role_id, :admin_perm_id, :now),
                           (:rp2_id, :admin_role_id, :maintainer_perm_id, :now),
                           (:rp3_id, :admin_role_id, :user_perm_id, :now)
                """),
                {
                    "rp1_id": str(uuid.uuid4()),
                    "rp2_id": str(uuid.uuid4()),
                    "rp3_id": str(uuid.uuid4()),
                    "admin_role_id": admin_role_id,
                    "admin_perm_id": admin_perm_id,
                    "maintainer_perm_id": maintainer_perm_id,
                    "user_perm_id": user_perm_id,
                    "now": now
                }
            )
        
        if maintainer_role_result:
            maintainer_role_id = maintainer_role_result[0]
            # Maintainer gets maintainer and user permissions
            connection.execute(
                sa.text("""
                    INSERT INTO rolepermission (id, role_id, permission_id, created_at) 
                    VALUES (:rp4_id, :maintainer_role_id, :maintainer_perm_id, :now),
                           (:rp5_id, :maintainer_role_id, :user_perm_id, :now)
                """),
                {
                    "rp4_id": str(uuid.uuid4()),
                    "rp5_id": str(uuid.uuid4()),
                    "maintainer_role_id": maintainer_role_id,
                    "maintainer_perm_id": maintainer_perm_id,
                    "user_perm_id": user_perm_id,
                    "now": now
                }
            )
        
        if user_role_result:
            user_role_id = user_role_result[0]
            # User gets only user permission
            connection.execute(
                sa.text("""
                    INSERT INTO rolepermission (id, role_id, permission_id, created_at) 
                    VALUES (:rp6_id, :user_role_id, :user_perm_id, :now)
                """),
                {
                    "rp6_id": str(uuid.uuid4()),
                    "user_role_id": user_role_id,
                    "user_perm_id": user_perm_id,
                    "now": now
                }
            )


def downgrade() -> None:
    # Remove specific permissions
    connection = op.get_bind()
    
    # Get permission IDs
    admin_perm_result = connection.execute(sa.text("SELECT id FROM permission WHERE name = 'list_all_users_admin'")).fetchone()
    maintainer_perm_result = connection.execute(sa.text("SELECT id FROM permission WHERE name = 'list_all_users_role_maintainer'")).fetchone()
    user_perm_result = connection.execute(sa.text("SELECT id FROM permission WHERE name = 'list_all_users_role_user'")).fetchone()
    
    if admin_perm_result:
        admin_perm_id = admin_perm_result[0]
        connection.execute(sa.text("DELETE FROM rolepermission WHERE permission_id = :perm_id"), {"perm_id": admin_perm_id})
        connection.execute(sa.text("DELETE FROM permission WHERE id = :perm_id"), {"perm_id": admin_perm_id})
    
    if maintainer_perm_result:
        maintainer_perm_id = maintainer_perm_result[0]
        connection.execute(sa.text("DELETE FROM rolepermission WHERE permission_id = :perm_id"), {"perm_id": maintainer_perm_id})
        connection.execute(sa.text("DELETE FROM permission WHERE id = :perm_id"), {"perm_id": maintainer_perm_id})
    
    if user_perm_result:
        user_perm_id = user_perm_result[0]
        connection.execute(sa.text("DELETE FROM rolepermission WHERE permission_id = :perm_id"), {"perm_id": user_perm_id})
        connection.execute(sa.text("DELETE FROM permission WHERE id = :perm_id"), {"perm_id": user_perm_id})