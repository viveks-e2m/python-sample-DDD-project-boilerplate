import pytest
from apps.user.application.service import UserApplicationService
from apps.user.application.schema import UserCreateModel, UserUpdateModel, UserLoginModel, UserPasswordResetModel


class TestUserApplicationService:
    """Test cases for UserApplicationService"""
    
    @pytest.fixture
    def user_service(self, session):
        """Create a UserApplicationService instance for testing"""
        return UserApplicationService(session)
    
    @pytest.fixture
    def sample_user_data(self):
        """Sample user data for testing"""
        return UserCreateModel(
            username="testuser",
            email="test@example.com",
            password="Test1234",
            first_name="Test",
            last_name="User"
        )
    
    @pytest.mark.asyncio
    async def test_register_user(self, user_service, sample_user_data):
        """Test registering a user"""
        user = await user_service.register_user(sample_user_data)
        
        assert user.username == "testuser"
        assert user.email == "test@example.com"
        assert user.first_name == "Test"
        assert user.last_name == "User"
        assert user.is_active is True
        assert user.is_superuser is False
    
    @pytest.mark.asyncio
    async def test_register_user_already_exists(self, user_service, sample_user_data):
        """Test registering a user that already exists"""
        # Register first user
        await user_service.register_user(sample_user_data)
        
        # Try to register the same user again
        with pytest.raises(Exception):  # Will be caught and re-raised as HTTPException
            await user_service.register_user(sample_user_data)
    
    @pytest.mark.asyncio
    async def test_get_user(self, user_service, sample_user_data):
        """Test retrieving a user by ID"""
        # Register user
        created_user = await user_service.register_user(sample_user_data)
        
        # Retrieve user
        retrieved_user = await user_service.get_user(created_user.id)
        
        assert retrieved_user.id == created_user.id
        assert retrieved_user.username == created_user.username
    
    @pytest.mark.asyncio
    async def test_get_user_not_found(self, user_service):
        """Test retrieving a non-existent user"""
        with pytest.raises(Exception):  # Will be caught and re-raised as HTTPException
            await user_service.get_user(99999)
    
    @pytest.mark.asyncio
    async def test_update_user(self, user_service, sample_user_data):
        """Test updating a user"""
        # Register user
        created_user = await user_service.register_user(sample_user_data)
        
        # Update user
        update_data = UserUpdateModel(
            email="updated@example.com",
            first_name="Updated"
        )
        
        # Create a mock current user for testing
        class MockUser:
            def __init__(self, user_id):
                self.id = user_id
                self.is_superuser = False
        
        current_user = MockUser(created_user.id)
        
        updated_user = await user_service.update_user(created_user.id, update_data, current_user)
        
        assert updated_user.email == "updated@example.com"
        assert updated_user.first_name == "Updated"
    
    @pytest.mark.asyncio
    async def test_update_user_not_found(self, user_service):
        """Test updating a non-existent user"""
        update_data = UserUpdateModel(
            email="updated@example.com"
        )
        
        # Create a mock current user for testing
        class MockUser:
            def __init__(self, user_id):
                self.id = user_id
                self.is_superuser = False
        
        current_user = MockUser(1)
        
        with pytest.raises(Exception):  # Will be caught and re-raised as HTTPException
            await user_service.update_user(99999, update_data, current_user)
    
    @pytest.mark.asyncio
    async def test_delete_user(self, user_service, sample_user_data):
        """Test deleting a user"""
        # Register user
        created_user = await user_service.register_user(sample_user_data)
        
        # Create a mock current user for testing
        class MockUser:
            def __init__(self, user_id):
                self.id = user_id
                self.is_superuser = False
        
        current_user = MockUser(created_user.id)
        
        # Delete user
        deleted_user = await user_service.delete_user(created_user.id, current_user)
        
        assert deleted_user.is_active is False
    
    @pytest.mark.asyncio
    async def test_delete_user_not_found(self, user_service):
        """Test deleting a non-existent user"""
        # Create a mock current user for testing
        class MockUser:
            def __init__(self, user_id):
                self.id = user_id
                self.is_superuser = False
        
        current_user = MockUser(1)
        
        with pytest.raises(Exception):  # Will be caught and re-raised as HTTPException
            await user_service.delete_user(99999, current_user)
    
    @pytest.mark.asyncio
    async def test_login_user(self, user_service, sample_user_data):
        """Test logging in a user"""
        # Register user
        await user_service.register_user(sample_user_data)
        
        # Login user
        login_data = UserLoginModel(
            username="testuser",
            password="Test1234"
        )
        
        authenticated_user = await user_service.login_user(login_data)
        
        assert authenticated_user.username == "testuser"
    
    @pytest.mark.asyncio
    async def test_login_user_wrong_credentials(self, user_service, sample_user_data):
        """Test logging in with wrong credentials"""
        # Register user
        await user_service.register_user(sample_user_data)
        
        # Login with wrong password
        login_data = UserLoginModel(
            username="testuser",
            password="WrongPassword"
        )
        
        with pytest.raises(Exception):  # Will be caught and re-raised as HTTPException
            await user_service.login_user(login_data)
    
    @pytest.mark.asyncio
    async def test_reset_password(self, user_service, sample_user_data):
        """Test resetting a user's password"""
        # Register user
        await user_service.register_user(sample_user_data)
        
        # Reset password
        reset_data = UserPasswordResetModel(
            email="test@example.com"
        )
        
        await user_service.reset_password(reset_data, "NewPass123")
        
        # Login with new password
        login_data = UserLoginModel(
            username="testuser",
            password="NewPass123"
        )
        
        authenticated_user = await user_service.login_user(login_data)
        assert authenticated_user.username == "testuser"
    
    @pytest.mark.asyncio
    async def test_reset_password_user_not_found(self, user_service):
        """Test resetting password for a non-existent user"""
        reset_data = UserPasswordResetModel(
            email="nonexistent@example.com"
        )
        
        with pytest.raises(Exception):  # Will be caught and re-raised as HTTPException
            await user_service.reset_password(reset_data, "NewPass123")