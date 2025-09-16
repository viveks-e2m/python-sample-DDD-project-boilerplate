import pytest
from unittest.mock import Mock, AsyncMock, patch
from apps.demo.application.service import DemoItemApplicationService
from apps.demo.application.schemas import DemoCreateModel, DemoUpdateModel


class TestDemoApplicationService:
    
    @pytest.mark.asyncio
    async def test_create_demo_item(self):
        """Test creating a demo item through application service"""
        # Arrange
        demo_data = DemoCreateModel(
            title="Test Item",
            description="Test Description",
            priority=1
        )
        session_mock = AsyncMock()
        user_mock = Mock()
        user_mock.username = "testuser"
        
        # Create service instance
        service = DemoItemApplicationService(session_mock)
        
        # Mock the domain service
        with patch.object(service.domain_service, 'create_demo_item') as mock_create:
            mock_create.return_value = Mock()
            
            # Act
            result = await service.create_demo_item(demo_data, user_mock)
            
            # Assert
            mock_create.assert_called_once_with(demo_data, user_mock)
            
    @pytest.mark.asyncio
    async def test_get_demo_item(self):
        """Test retrieving a demo item through application service"""
        # Arrange
        demo_id = 1
        session_mock = AsyncMock()
        
        # Create service instance
        service = DemoItemApplicationService(session_mock)
        
        # Mock the domain service
        with patch.object(service.domain_service, 'get_demo_item') as mock_get:
            mock_get.return_value = Mock()
            
            # Act
            result = await service.get_demo_item(demo_id)
            
            # Assert
            mock_get.assert_called_once_with(demo_id)
            
    @pytest.mark.asyncio
    async def test_update_demo_item(self):
        """Test updating a demo item through application service"""
        # Arrange
        demo_id = 1
        update_data = DemoUpdateModel(
            title="Updated Title"
        )
        session_mock = AsyncMock()
        user_mock = Mock()
        user_mock.username = "testuser"
        
        # Create service instance
        service = DemoItemApplicationService(session_mock)
        
        # Mock the domain service
        with patch.object(service.domain_service, 'update_demo_item') as mock_update:
            mock_update.return_value = Mock()
            
            # Act
            result = await service.update_demo_item(demo_id, update_data, user_mock)
            
            # Assert
            mock_update.assert_called_once_with(demo_id, update_data, user_mock)
            
    @pytest.mark.asyncio
    async def test_delete_demo_item(self):
        """Test deleting a demo item through application service"""
        # Arrange
        demo_id = 1
        session_mock = AsyncMock()
        user_mock = Mock()
        user_mock.username = "testuser"
        
        # Create service instance
        service = DemoItemApplicationService(session_mock)
        
        # Mock the domain service
        with patch.object(service.domain_service, 'delete_demo_item') as mock_delete:
            mock_delete.return_value = Mock()
            
            # Act
            result = await service.delete_demo_item(demo_id, user_mock)
            
            # Assert
            mock_delete.assert_called_once_with(demo_id, user_mock)