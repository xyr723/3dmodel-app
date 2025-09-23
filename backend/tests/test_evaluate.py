"""
模型评估API测试
"""
import pytest
from unittest.mock import Mock, patch
from fastapi.testclient import TestClient

from app.main import app
from app.models.request import EvaluateRequest, FeedbackRequest


@pytest.fixture
def client():
    """测试客户端"""
    return TestClient(app)


@pytest.fixture
def sample_evaluate_request():
    """示例评估请求"""
    return {
        "task_id": "test_task_123",
        "metrics": {
            "geometry_quality": 0.85,
            "texture_quality": 0.90,
            "file_size": 25.5
        },
        "auto_evaluate": True,
        "check_geometry": True,
        "check_texture": True,
        "check_topology": True
    }


@pytest.fixture
def sample_feedback_request():
    """示例反馈请求"""
    return {
        "task_id": "test_task_123",
        "user_id": "user_456",
        "rating": 4,
        "comment": "模型质量很好，但纹理可以更细致",
        "feedback_type": "quality",
        "quality_rating": 4,
        "accuracy_rating": 5,
        "speed_rating": 3,
        "issues": ["texture_resolution"],
        "suggestions": "提高纹理分辨率"
    }


@pytest.fixture
def mock_api_key():
    """模拟API密钥"""
    return "test_api_key_12345"


class TestEvaluateAPI:
    """评估API测试类"""
    
    def test_evaluate_request_validation(self):
        """测试评估请求参数验证"""
        # 有效请求
        valid_request = EvaluateRequest(
            task_id="test_task_123",
            metrics={"geometry_quality": 0.85}
        )
        assert valid_request.task_id == "test_task_123"
        assert valid_request.auto_evaluate is True
        
        # 无效请求 - 短任务ID
        with pytest.raises(ValueError):
            EvaluateRequest(task_id="short")
    
    def test_feedback_request_validation(self):
        """测试反馈请求参数验证"""
        # 有效请求
        valid_request = FeedbackRequest(
            task_id="test_task_123",
            rating=4,
            comment="很好"
        )
        assert valid_request.task_id == "test_task_123"
        assert valid_request.rating == 4
        
        # 无效请求 - 评分超出范围
        with pytest.raises(ValueError):
            FeedbackRequest(
                task_id="test_task_123",
                rating=6  # 超出1-5范围
            )
    
    @patch('app.core.security.verify_api_key')
    @patch('app.db.feedback.FeedbackDB.save_evaluation')
    def test_evaluate_model_success(self, mock_save_eval, mock_verify_api, client, sample_evaluate_request, mock_api_key):
        """测试成功评估模型"""
        # 设置模拟
        mock_verify_api.return_value = mock_api_key
        mock_save_eval.return_value = {"evaluation_id": "eval_123"}
        
        # 发送请求
        response = client.post(
            "/api/evaluate",
            json=sample_evaluate_request,
            headers={"Authorization": f"Bearer {mock_api_key}"}
        )
        
        # 验证响应
        assert response.status_code == 200
        data = response.json()
        assert data["task_id"] == "test_task_123"
        assert data["evaluation_id"] == "eval_123"
        assert "score" in data
        assert data["message"] == "评估完成"
    
    @patch('app.core.security.verify_api_key')
    def test_evaluate_model_unauthorized(self, mock_verify_api, client, sample_evaluate_request):
        """测试未授权评估"""
        mock_verify_api.side_effect = Exception("无效的API密钥")
        
        response = client.post(
            "/api/evaluate",
            json=sample_evaluate_request,
            headers={"Authorization": "Bearer invalid_key"}
        )
        
        assert response.status_code == 401
    
    @patch('app.core.security.verify_api_key')
    @patch('app.db.feedback.FeedbackDB.save_feedback')
    def test_submit_feedback_success(self, mock_save_feedback, mock_verify_api, client, sample_feedback_request, mock_api_key):
        """测试成功提交反馈"""
        # 设置模拟
        mock_verify_api.return_value = mock_api_key
        mock_save_feedback.return_value = {"feedback_id": "feedback_123"}
        
        # 发送请求
        response = client.post(
            "/api/feedback",
            json=sample_feedback_request,
            headers={"Authorization": f"Bearer {mock_api_key}"}
        )
        
        # 验证响应
        assert response.status_code == 200
        data = response.json()
        assert data["feedback_id"] == "feedback_123"
        assert data["message"] == "反馈提交成功"
        assert data["status"] == "success"
    
    @patch('app.core.security.verify_api_key')
    @patch('app.db.feedback.FeedbackDB.get_feedback_by_task')
    def test_get_feedback_success(self, mock_get_feedback, mock_verify_api, client, mock_api_key):
        """测试成功获取反馈"""
        # 设置模拟
        mock_verify_api.return_value = mock_api_key
        mock_get_feedback.return_value = [
            {
                "id": "feedback_123",
                "task_id": "test_task_123",
                "rating": 4,
                "comment": "很好",
                "created_at": "2023-01-01T00:00:00"
            }
        ]
        
        # 发送请求
        response = client.get(
            "/api/feedback/test_task_123",
            headers={"Authorization": f"Bearer {mock_api_key}"}
        )
        
        # 验证响应
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["task_id"] == "test_task_123"
        assert data[0]["rating"] == 4
    
    @patch('app.core.security.verify_api_key')
    def test_submit_feedback_invalid_request(self, mock_verify_api, client, mock_api_key):
        """测试提交无效反馈"""
        mock_verify_api.return_value = mock_api_key
        
        invalid_request = {
            "task_id": "short",  # 太短的任务ID
            "rating": 6  # 超出范围的评分
        }
        
        response = client.post(
            "/api/feedback",
            json=invalid_request,
            headers={"Authorization": f"Bearer {mock_api_key}"}
        )
        
        assert response.status_code == 422  # 验证错误


class TestEvaluationLogic:
    """评估逻辑测试类"""
    
    @pytest.mark.asyncio
    async def test_calculate_model_quality_basic(self):
        """测试基础模型质量计算"""
        from app.api.evaluate import _calculate_model_quality
        
        request = EvaluateRequest(
            task_id="test_task_123",
            metrics={}
        )
        
        score = await _calculate_model_quality(request)
        
        # 基础分数应该是75.0
        assert score == 75.0
    
    @pytest.mark.asyncio
    async def test_calculate_model_quality_with_metrics(self):
        """测试带指标的模型质量计算"""
        from app.api.evaluate import _calculate_model_quality
        
        request = EvaluateRequest(
            task_id="test_task_123",
            metrics={
                "geometry_quality": 0.9,  # 应该加10分
                "texture_quality": 0.85,  # 应该加10分
                "file_size": 30  # 应该加5分
            }
        )
        
        score = await _calculate_model_quality(request)
        
        # 基础75 + 10 + 10 + 5 = 100
        assert score == 100.0
    
    @pytest.mark.asyncio
    async def test_calculate_model_quality_poor_metrics(self):
        """测试低质量指标的模型质量计算"""
        from app.api.evaluate import _calculate_model_quality
        
        request = EvaluateRequest(
            task_id="test_task_123",
            metrics={
                "geometry_quality": 0.5,  # 不加分
                "texture_quality": 0.6,   # 不加分
                "file_size": 100  # 不加分
            }
        )
        
        score = await _calculate_model_quality(request)
        
        # 只有基础分数75
        assert score == 75.0
    
    @pytest.mark.asyncio
    async def test_calculate_model_quality_bounds(self):
        """测试模型质量分数边界"""
        from app.api.evaluate import _calculate_model_quality
        
        # 测试上限
        request = EvaluateRequest(
            task_id="test_task_123",
            metrics={
                "geometry_quality": 1.0,
                "texture_quality": 1.0,
                "file_size": 1  # 非常小的文件
            }
        )
        
        score = await _calculate_model_quality(request)
        
        # 分数不应超过100
        assert score <= 100.0
        
        # 测试下限（虽然当前实现不会低于基础分数）
        assert score >= 0.0


if __name__ == "__main__":
    pytest.main([__file__])
