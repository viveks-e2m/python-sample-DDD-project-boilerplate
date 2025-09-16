from apps.demo.domain.models import DemoItem


import pytest
from unittest.mock import Mock, AsyncMock
from apps.demo.domain.service import DemoItemInstanceService
from apps.demo.application.schemas import DemoCreateModel, DemoUpdateModel


class TestDemoDomainService:
    
    @pytest.mark.asyncio
    async def test_create_demo_item(self):
        """Test creating a demo item"""
        # Arrange
        demo_data = DemoCreateModel(
            title="Test Item",
            description="Test Description",
            priority=1
        )
        session_mock = AsyncMock()
        user_mock = Mock()
        user_mock.username = "testuser"
        
        service: DemoItemInstanceService = DemoItemInstanceService(session_mock)
        
        # Act
        result: DemoItem = await service.create_demo_item(demo_data, user_mock)
        
        # Assert
        assert result is not None
        session_mock.add.assert_called_once()
        session_mock.commit.assert_called_once()
        session_mock.refresh.assert_called_once()
        
    @pytest.mark.asyncio
    async def test_get_demo_item(self):
        """Test retrieving a demo item"""
        # Arrange
        demo_id = 1
        session_mock: AsyncMock = AsyncMock()
        expected_item: Mock = Mock()
        session_mock.exec.return_value.first.return_value = expected_item
        
        service: DemoItemInstanceService = DemoItemInstanceService(session_mock)
        
        # Act
        result = await service.get_demo_item(demo_id)
        
        # Assert
        assert result == expected_item
        session_mock.exec.assert_called_once()
        
    @pytest.mark.asyncio
    async def test_update_demo_item(self):
        """Test updating a demo item"""
        # Arrange
        demo_id = 1
        update_data = DemoUpdateModel(
            title="Updated Title"
        )
        session_mock = AsyncMock()
        demo_item_mock = Mock()
        demo_item_mock.created_by = "testuser"
        session_mock.exec.return_value.first.return_value = demo_item_mock
        user_mock = Mock()
        user_mock.username = "testuser"
        user_mock.is_superuser = False
        
        service = DemoItemInstanceService(session_mock)
        
        # Act
        result = await service.update_demo_item(demo_id, update_data, user_mock)
        
        # Assert
        assert result == demo_item_mock
        assert demo_item_mock.title == "Updated Title"
        session_mock.add.assert_called_once()
        session_mock.commit.assert_called_once()
        session_mock.refresh.assert_called_once()