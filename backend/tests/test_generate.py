"""
3D模型生成API测试
"""
import pytest
import asyncio
from unittest.mock import Mock, patch
from fastapi.testclient import TestClient

from app.main import app
from app.models.request import GenerateRequest, ModelStyle, GenerationMode
from app.services.model_service import ModelService


@pytest.fixture
def client():
    """测试客户端"""
    return TestClient(app)


@pytest.fixture
def sample_generate_request():
    """示例生成请求"""
    return {
        "prompt": "一只可爱的小猫",
        "style": "realistic",
        "mode": "text_to_3d",
        "quality": "medium",
        "resolution": 512,
        "output_format": "obj",
        "include_texture": True
    }


@pytest.fixture
def mock_api_key():
    """模拟API密钥"""
    return "test_api_key_12345"


class TestGenerateAPI:
    """生成API测试类"""
    
    def test_generate_request_validation(self):
        """测试请求参数验证"""
        # 有效请求
        valid_request = GenerateRequest(
            prompt="一只小猫",
            style=ModelStyle.REALISTIC,
            mode=GenerationMode.TEXT_TO_3D
        )
        assert valid_request.prompt == "一只小猫"
        assert valid_request.style == ModelStyle.REALISTIC
        
        # 无效请求 - 空提示词
        with pytest.raises(ValueError):
            GenerateRequest(
                prompt="",
                style=ModelStyle.REALISTIC,
                mode=GenerationMode.TEXT_TO_3D
            )
    
    @patch('app.core.security.verify_api_key')
    @patch('app.services.model_service.ModelService.generate_model')
    def test_generate_3d_model_success(self, mock_generate, mock_verify_api, client, sample_generate_request, mock_api_key):
        """测试成功生成3D模型"""
        # 设置模拟
        mock_verify_api.return_value = mock_api_key
        mock_generate.return_value = Mock(
            task_id="test_task_123",
            status="completed",
            message="生成完成",
            model_url="https://example.com/model.obj"
        )
        
        # 发送请求
        response = client.post(
            "/api/generate",
            json=sample_generate_request,
            headers={"Authorization": f"Bearer {mock_api_key}"}
        )
        
        # 验证响应
        assert response.status_code == 200
        data = response.json()
        assert data["task_id"] == "test_task_123"
        assert data["status"] == "completed"
        assert "model_url" in data
    
    @patch('app.core.security.verify_api_key')
    def test_generate_3d_model_unauthorized(self, mock_verify_api, client, sample_generate_request):
        """测试未授权访问"""
        mock_verify_api.side_effect = Exception("无效的API密钥")
        
        response = client.post(
            "/api/generate",
            json=sample_generate_request,
            headers={"Authorization": "Bearer invalid_key"}
        )
        
        assert response.status_code == 401
    
    def test_generate_3d_model_missing_auth(self, client, sample_generate_request):
        """测试缺少认证信息"""
        response = client.post(
            "/api/generate",
            json=sample_generate_request
        )
        
        assert response.status_code == 401
    
    @patch('app.core.security.verify_api_key')
    def test_generate_3d_model_invalid_request(self, mock_verify_api, client, mock_api_key):
        """测试无效请求参数"""
        mock_verify_api.return_value = mock_api_key
        
        invalid_request = {
            "prompt": "",  # 空提示词
            "style": "invalid_style"
        }
        
        response = client.post(
            "/api/generate",
            json=invalid_request,
            headers={"Authorization": f"Bearer {mock_api_key}"}
        )
        
        assert response.status_code == 422  # 验证错误
    
    @patch('app.core.security.verify_api_key')
    @patch('app.services.model_service.ModelService.get_task_status')
    def test_get_generation_status(self, mock_get_status, mock_verify_api, client, mock_api_key):
        """测试获取生成状态"""
        mock_verify_api.return_value = mock_api_key
        mock_get_status.return_value = {
            "task_id": "test_task_123",
            "status": "processing",
            "progress": 50.0,
            "message": "正在生成中"
        }
        
        response = client.get(
            "/api/generate/status/test_task_123",
            headers={"Authorization": f"Bearer {mock_api_key}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["task_id"] == "test_task_123"
        assert data["status"] == "processing"
        assert data["progress"] == 50.0
    
    @patch('app.core.security.verify_api_key')
    @patch('app.services.model_service.ModelService.get_task_status')
    def test_get_generation_status_not_found(self, mock_get_status, mock_verify_api, client, mock_api_key):
        """测试获取不存在的任务状态"""
        mock_verify_api.return_value = mock_api_key
        mock_get_status.return_value = None
        
        response = client.get(
            "/api/generate/status/nonexistent_task",
            headers={"Authorization": f"Bearer {mock_api_key}"}
        )
        
        assert response.status_code == 404
    
    @patch('app.core.security.verify_api_key')
    @patch('app.services.model_service.ModelService.get_model_file')
    def test_download_model(self, mock_get_file, mock_verify_api, client, mock_api_key):
        """测试下载模型文件"""
        mock_verify_api.return_value = mock_api_key
        mock_get_file.return_value = "/path/to/model.obj"
        
        with patch('fastapi.responses.FileResponse') as mock_file_response:
            response = client.get(
                "/api/generate/download/test_task_123",
                headers={"Authorization": f"Bearer {mock_api_key}"}
            )
            
            mock_file_response.assert_called_once()
    
    @patch('app.core.security.verify_api_key')
    @patch('app.services.model_service.ModelService.get_model_file')
    def test_download_model_not_found(self, mock_get_file, mock_verify_api, client, mock_api_key):
        """测试下载不存在的模型文件"""
        mock_verify_api.return_value = mock_api_key
        mock_get_file.return_value = None
        
        response = client.get(
            "/api/generate/download/nonexistent_task",
            headers={"Authorization": f"Bearer {mock_api_key}"}
        )
        
        assert response.status_code == 404


class TestModelService:
    """模型服务测试类"""
    
    @pytest.fixture
    def model_service(self):
        """模型服务实例"""
        return ModelService()
    
    @pytest.fixture
    def sample_request(self):
        """示例请求"""
        return GenerateRequest(
            prompt="一只小猫",
            style=ModelStyle.REALISTIC,
            mode=GenerationMode.TEXT_TO_3D
        )
    
    @pytest.mark.asyncio
    async def test_generate_model_meshy_provider(self, model_service, sample_request):
        """测试使用Meshy提供商生成模型"""
        with patch.object(model_service, '_generate_with_meshy') as mock_generate:
            mock_generate.return_value = Mock(
                task_id="test_123",
                status="completed"
            )
            
            result = await model_service.generate_model(sample_request)
            
            assert result.task_id == "test_123"
            assert result.status == "completed"
            mock_generate.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_task_status(self, model_service):
        """测试获取任务状态"""
        # 添加测试任务
        task_id = "test_task_123"
        model_service.tasks[task_id] = {
            "task_id": task_id,
            "status": "processing",
            "progress": 30.0,
            "created_at": "2023-01-01T00:00:00"
        }
        
        status = await model_service.get_task_status(task_id)
        
        assert status is not None
        assert status["task_id"] == task_id
        assert status["status"] == "processing"
        assert status["progress"] == 30.0
    
    @pytest.mark.asyncio
    async def test_get_task_status_not_found(self, model_service):
        """测试获取不存在的任务状态"""
        status = await model_service.get_task_status("nonexistent_task")
        assert status is None
    
    @pytest.mark.asyncio
    async def test_cancel_task(self, model_service):
        """测试取消任务"""
        # 添加测试任务
        task_id = "test_task_123"
        model_service.tasks[task_id] = {
            "task_id": task_id,
            "status": "processing",
            "created_at": "2023-01-01T00:00:00"
        }
        
        result = await model_service.cancel_task(task_id)
        
        assert result is True
        assert model_service.tasks[task_id]["status"] == "cancelled"
    
    @pytest.mark.asyncio
    async def test_cancel_nonexistent_task(self, model_service):
        """测试取消不存在的任务"""
        result = await model_service.cancel_task("nonexistent_task")
        assert result is False


if __name__ == "__main__":
    pytest.main([__file__])
