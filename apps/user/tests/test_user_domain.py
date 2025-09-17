import pytest
from apps.user.domain.service import UserDomainService
from apps.user.domain.models import User
from apps.user.application.schema import UserCreateModel, UserUpdateModel, UserLoginModel
from apps.user.domain.exceptions import (
    UserNotFoundError, 
    UserAuthenticationError, 
    UserAlreadyExistsError,
    UserValidationError
)


class TestUserDomainService:
    """Test cases for UserDomainService"""
    
    @pytest.fixture
    def user_service(self, session):
        """Create a UserDomainService instance for testing"""
        return UserDomainService(session)
    
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
    async def test_create_user(self, user_service, sample_user_data):
        """Test creating a user"""
        user = await user_service.create_user(sample_user_data)
        
        assert user.username == "testuser"
        assert user.email == "test@example.com"
        assert user.first_name == "Test"
        assert user.last_name == "User"
        assert user.is_active is True
        assert user.is_superuser is False
        assert user.check_password("Test1234") is True
    
    @pytest.mark.asyncio
    async def test_create_user_already_exists_username(self, user_service, sample_user_data):
        """Test creating a user with an existing username"""
        # Create first user
        await user_service.create_user(sample_user_data)
        
        # Try to create another user with the same username
        with pytest.raises(UserAlreadyExistsError):
            await user_service.create_user(sample_user_data)
    
    @pytest.mark.asyncio
    async def test_create_user_already_exists_email(self, user_service, sample_user_data):
        """Test creating a user with an existing email"""
        # Create first user
        await user_service.create_user(sample_user_data)
        
        # Create another user data with different username but same email
        new_user_data = UserCreateModel(
            username="newuser",
            email="test@example.com",
            password="Test1234",
            first_name="New",
            last_name="User"
        )
        
        with pytest.raises(UserAlreadyExistsError):
            await user_service.create_user(new_user_data)
    
    @pytest.mark.asyncio
    async def test_get_user(self, user_service, sample_user_data):
        """Test retrieving a user by ID"""
        # Create user
        created_user = await user_service.create_user(sample_user_data)
        
        # Retrieve user
        retrieved_user = await user_service.get_user(created_user.id)
        
        assert retrieved_user.id == created_user.id
        assert retrieved_user.username == created_user.username
        assert retrieved_user.email == created_user.email
    
    @pytest.mark.asyncio
    async def test_get_user_not_found(self, user_service):
        """Test retrieving a non-existent user"""
        with pytest.raises(UserNotFoundError):
            await user_service.get_user(99999)
    
    @pytest.mark.asyncio
    async def test_get_user_by_username(self, user_service, sample_user_data):
        """Test retrieving a user by username"""
        # Create user
        created_user = await user_service.create_user(sample_user_data)
        
        # Retrieve user by username
        retrieved_user = await user_service.get_user_by_username("testuser")
        
        assert retrieved_user.username == "testuser"
        assert retrieved_user.email == "test@example.com"
    
    @pytest.mark.asyncio
    async def test_get_user_by_username_not_found(self, user_service):
        """Test retrieving a non-existent user by username"""
        with pytest.raises(UserNotFoundError):
            await user_service.get_user_by_username("nonexistent")
    
    @pytest.mark.asyncio
    async def test_update_user(self, user_service, sample_user_data):
        """Test updating a user"""
        # Create user
        created_user = await user_service.create_user(sample_user_data)
        
        # Update user
        update_data = UserUpdateModel(
            email="updated@example.com",
            first_name="Updated",
            last_name="Name"
        )
        
        updated_user = await user_service.update_user(created_user.id, update_data)
        
        assert updated_user.email == "updated@example.com"
        assert updated_user.first_name == "Updated"
        assert updated_user.last_name == "Name"
    
    @pytest.mark.asyncio
    async def test_update_user_not_found(self, user_service):
        """Test updating a non-existent user"""
        update_data = UserUpdateModel(
            email="updated@example.com"
        )
        
        with pytest.raises(UserNotFoundError):
            await user_service.update_user(99999, update_data)
    
    @pytest.mark.asyncio
    async def test_update_user_email_already_taken(self, user_service, sample_user_data):
        """Test updating a user with an email that's already taken"""
        # Create first user
        await user_service.create_user(sample_user_data)
        
        # Create second user
        second_user_data = UserCreateModel(
            username="seconduser",
            email="second@example.com",
            password="Test1234",
            first_name="Second",
            last_name="User"
        )
        second_user = await user_service.create_user(second_user_data)
        
        # Try to update second user with first user's email
        update_data = UserUpdateModel(
            email="test@example.com"
        )
        
        with pytest.raises(UserValidationError):
            await user_service.update_user(second_user.id, update_data)
    
    @pytest.mark.asyncio
    async def test_delete_user(self, user_service, sample_user_data):
        """Test deleting a user (soft delete)"""
        # Create user
        created_user = await user_service.create_user(sample_user_data)
        
        # Delete user
        deleted_user = await user_service.delete_user(created_user.id)
        
        assert deleted_user.is_active is False
    
    @pytest.mark.asyncio
    async def test_delete_user_not_found(self, user_service):
        """Test deleting a non-existent user"""
        with pytest.raises(UserNotFoundError):
            await user_service.delete_user(99999)
    
    @pytest.mark.asyncio
    async def test_authenticate_user(self, user_service, sample_user_data):
        """Test authenticating a user"""
        # Create user
        await user_service.create_user(sample_user_data)
        
        # Authenticate user
        login_data = UserLoginModel(
            username="testuser",
            password="Test1234"
        )
        
        authenticated_user = await user_service.authenticate_user(login_data)
        
        assert authenticated_user.username == "testuser"
    
    @pytest.mark.asyncio
    async def test_authenticate_user_wrong_password(self, user_service, sample_user_data):
        """Test authenticating a user with wrong password"""
        # Create user
        await user_service.create_user(sample_user_data)
        
        # Authenticate user with wrong password
        login_data = UserLoginModel(
            username="testuser",
            password="WrongPassword"
        )
        
        with pytest.raises(UserAuthenticationError):
            await user_service.authenticate_user(login_data)
    
    @pytest.mark.asyncio
    async def test_authenticate_user_not_found(self, user_service):
        """Test authenticating a non-existent user"""
        login_data = UserLoginModel(
            username="nonexistent",
            password="Test1234"
        )
        
        with pytest.raises(UserNotFoundError):
            await user_service.authenticate_user(login_data)
    
    @pytest.mark.asyncio
    async def test_reset_password(self, user_service, sample_user_data):
        """Test resetting a user's password"""
        # Create user
        created_user = await user_service.create_user(sample_user_data)
        
        # Reset password
        await user_service.reset_password("test@example.com", "NewPass123")
        
        # Authenticate with new password
        login_data = UserLoginModel(
            username="testuser",
            password="NewPass123"
        )
        
        authenticated_user = await user_service.authenticate_user(login_data)
        assert authenticated_user.username == "testuser"
    
    @pytest.mark.asyncio
    async def test_reset_password_user_not_found(self, user_service):
        """Test resetting password for a non-existent user"""
        with pytest.raises(UserNotFoundError):
            await user_service.reset_password("nonexistent@example.com", "NewPass123")