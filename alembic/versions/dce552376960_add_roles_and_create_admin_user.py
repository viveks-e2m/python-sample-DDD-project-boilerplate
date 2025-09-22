"""add_roles_and_create_admin_user

Revision ID: dce552376960
Revises: b7e12ebdc415
Create Date: 2025-09-22 17:48:11.843684

"""
from typing import Sequence, Union
import uuid
from datetime import datetime, timezone
import hashlib

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'dce552376960'
down_revision: Union[str, None] = 'b7e12ebdc415'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Check if roles already exist
    connection = op.get_bind()
    
    # Check if Admin role exists
    result = connection.execute(sa.text("SELECT COUNT(*) FROM role WHERE name = 'Admin'")).fetchone()
    if result is not None and result[0] == 0:
        now = datetime.now(timezone.utc)
        
        # Insert default roles using raw SQL
        admin_id = str(uuid.uuid4())
        maintainer_id = str(uuid.uuid4())
        user_id = str(uuid.uuid4())
        
        connection.execute(
            sa.text("""
                INSERT INTO role (id, name, description, created_at, updated_at) 
                VALUES (:admin_id, 'Admin', 'Administrator with full access', :now, :now),
                       (:maintainer_id, 'Maintainer', 'Maintainer with moderate access', :now, :now),
                       (:user_id, 'User', 'Regular user with limited access', :now, :now)
            """),
            {
                "admin_id": admin_id,
                "maintainer_id": maintainer_id,
                "user_id": user_id,
                "now": now
            }
        )
        
        # Check if permissions table is empty and insert some default permissions
        result = connection.execute(sa.text("SELECT COUNT(*) FROM permission")).fetchone()
        if result is not None and result[0] == 0:
            # Insert permissions
            list_users_id = str(uuid.uuid4())
            create_user_id = str(uuid.uuid4())
            update_user_id = str(uuid.uuid4())
            delete_user_id = str(uuid.uuid4())
            
            connection.execute(
                sa.text("""
                    INSERT INTO permission (id, name, description, created_at, updated_at) 
                    VALUES (:list_users_id, 'list_users', 'Permission to list users', :now, :now),
                           (:create_user_id, 'create_user', 'Permission to create users', :now, :now),
                           (:update_user_id, 'update_user', 'Permission to update users', :now, :now),
                           (:delete_user_id, 'delete_user', 'Permission to delete users', :now, :now)
                """),
                {
                    "list_users_id": list_users_id,
                    "create_user_id": create_user_id,
                    "update_user_id": update_user_id,
                    "delete_user_id": delete_user_id,
                    "now": now
                }
            )
            
            # Assign permissions to roles using raw SQL
            # Admin role gets all permissions
            connection.execute(
                sa.text("""
                    INSERT INTO rolepermission (id, role_id, permission_id, created_at) 
                    VALUES (:rp1_id, :admin_id, :list_users_id, :now),
                           (:rp2_id, :admin_id, :create_user_id, :now),
                           (:rp3_id, :admin_id, :update_user_id, :now),
                           (:rp4_id, :admin_id, :delete_user_id, :now)
                """),
                {
                    "rp1_id": str(uuid.uuid4()),
                    "rp2_id": str(uuid.uuid4()),
                    "rp3_id": str(uuid.uuid4()),
                    "rp4_id": str(uuid.uuid4()),
                    "admin_id": admin_id,
                    "list_users_id": list_users_id,
                    "create_user_id": create_user_id,
                    "update_user_id": update_user_id,
                    "delete_user_id": delete_user_id,
                    "now": now
                }
            )
            
            # Maintainer role gets list, create, update permissions
            connection.execute(
                sa.text("""
                    INSERT INTO rolepermission (id, role_id, permission_id, created_at) 
                    VALUES (:rp5_id, :maintainer_id, :list_users_id, :now),
                           (:rp6_id, :maintainer_id, :create_user_id, :now),
                           (:rp7_id, :maintainer_id, :update_user_id, :now)
                """),
                {
                    "rp5_id": str(uuid.uuid4()),
                    "rp6_id": str(uuid.uuid4()),
                    "rp7_id": str(uuid.uuid4()),
                    "maintainer_id": maintainer_id,
                    "list_users_id": list_users_id,
                    "create_user_id": create_user_id,
                    "update_user_id": update_user_id,
                    "now": now
                }
            )
            
            # User role gets only list permission
            connection.execute(
                sa.text("""
                    INSERT INTO rolepermission (id, role_id, permission_id, created_at) 
                    VALUES (:rp8_id, :user_id, :list_users_id, :now)
                """),
                {
                    "rp8_id": str(uuid.uuid4()),
                    "user_id": user_id,
                    "list_users_id": list_users_id,
                    "now": now
                }
            )
        
        # Check if admin user exists
        result = connection.execute(sa.text("SELECT COUNT(*) FROM user WHERE username = 'admin'")).fetchone()
        if result is not None and result[0] == 0:
            # Create admin user
            # Hash the password
            password_hash = hashlib.sha256("admin123".encode()).hexdigest()
            
            connection.execute(
                sa.text("""
                    INSERT INTO user (id, username, email, password, first_name, last_name, is_active, is_superuser, role_id, created_at, updated_at) 
                    VALUES (:user_id, 'admin', 'admin@example.com', '13November200@', 'Admin', 'User', 1, 1, :admin_role_id, :now, :now)
                """),
                {
                    "user_id": str(uuid.uuid4()),
                    "password": password_hash,
                    "admin_role_id": admin_id,
                    "now": now
                }
            )


def downgrade() -> None:
    # This is a data-only migration, so we don't need to drop tables
    # In a real scenario, you might want to remove the inserted data
    pass