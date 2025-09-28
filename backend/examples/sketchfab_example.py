"""
Sketchfab API使用示例
"""
import asyncio
import aiohttp
from typing import Dict, Any


class SketchfabAPIExample:
    """Sketchfab API使用示例类"""
    
    def __init__(self, base_url: str = "http://localhost:8000", api_key: str = "your-api-key"):
        self.base_url = base_url
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    
    async def search_models(self, query: str, **kwargs) -> Dict[str, Any]:
        """搜索3D模型"""
        url = f"{self.base_url}/api/sketchfab/search"
        
        # 构建搜索参数
        params = {
            "query": query,
            **kwargs
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, headers=self.headers) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    print(f"搜索失败: {response.status}")
                    return {}
    
    async def get_model_details(self, model_uid: str) -> Dict[str, Any]:
        """获取模型详情"""
        url = f"{self.base_url}/api/sketchfab/model/{model_uid}"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=self.headers) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    print(f"获取模型详情失败: {response.status}")
                    return {}
    
    async def download_model(self, model_uid: str, format: str = "original") -> Dict[str, Any]:
        """下载模型"""
        url = f"{self.base_url}/api/sketchfab/download/{model_uid}"
        params = {"format": format}
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, headers=self.headers) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    print(f"下载模型失败: {response.status}")
                    return {}
    
    async def get_popular_models(self, category: str = None, limit: int = 1) -> Dict[str, Any]:
        """获取热门模型"""
        url = f"{self.base_url}/api/sketchfab/popular"
        params = {"limit": limit}
        if category:
            params["category"] = category
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, headers=self.headers) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    print(f"获取热门模型失败: {response.status}")
                    return {}


async def main():
    """主函数示例"""
    
    # 初始化API客户端
    api = SketchfabAPIExample(
        base_url="http://localhost:8000",
        api_key="your-api-key-here"  # 替换为你的API密钥
    )
    
    print("=== Sketchfab API 使用示例 ===\n")
    
    # 1. 搜索汽车模型
    print("1. 搜索汽车模型...")
    search_result = await api.search_models(
        query="car",
        category="vehicles",
        downloadable=True,
        per_page=5
    )
    
    if search_result and "models" in search_result:
        print(f"找到 {search_result['total_count']} 个汽车模型")
        for i, model in enumerate(search_result["models"][:3], 1):
            print(f"  {i}. {model['name']} - 作者: {model['author']}")
            print(f"     面数: {model.get('face_count', 'N/A')}, 可下载: {model['downloadable']}")
    
    print("\n" + "="*50 + "\n")
    
    # 2. 获取热门角色模型
    print("2. 获取热门角色模型...")
    popular_result = await api.get_popular_models(category="characters", limit=1)
    
    if popular_result:
        print(f"热门角色模型:")
        for i, model in enumerate(popular_result[:3], 1):
            print(f"  {i}. {model['name']} - 作者: {model['author']}")
            print(f"     点赞数: {model.get('like_count', 'N/A')}, 浏览数: {model.get('view_count', 'N/A')}")
    
    print("\n" + "="*50 + "\n")
    
    # 3. 获取特定模型详情（使用搜索结果中的第一个模型）
    if search_result and "models" in search_result and search_result["models"]:
        model_uid = search_result["models"][0]["uid"]
        print(f"3. 获取模型详情: {model_uid}")
        
        model_details = await api.get_model_details(model_uid)
        if model_details:
            print(f"  模型名称: {model_details['name']}")
            print(f"  作者: {model_details['author']}")
            print(f"  描述: {model_details.get('description', 'N/A')[:100]}...")
            print(f"  许可证: {model_details.get('license', 'N/A')}")
            print(f"  面数: {model_details.get('face_count', 'N/A')}")
            print(f"  可下载: {model_details['downloadable']}")
        
        print("\n" + "="*50 + "\n")
        
        # 4. 尝试下载模型（如果可下载）
        if model_details and model_details.get('downloadable'):
            print(f"4. 尝试下载模型: {model_uid}")
            
            download_result = await api.download_model(model_uid)
            if download_result and download_result.get('status') == 'success':
                print(f"  下载链接生成成功!")
                print(f"  下载URL: {download_result.get('download_url', 'N/A')}")
                print(f"  文件格式: {download_result.get('file_format', 'N/A')}")
                print(f"  许可证要求: {'需要署名' if download_result.get('attribution_required') else '无需署名'}")
                print(f"  商业使用: {'允许' if download_result.get('commercial_use') else '不允许'}")
            else:
                print(f"  下载失败: {download_result.get('message', 'Unknown error')}")
        else:
            print("4. 该模型不支持下载")
    
    print("\n=== 示例完成 ===")


if __name__ == "__main__":
    # 运行示例
    asyncio.run(main())
