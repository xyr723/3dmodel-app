"""
文件处理相关工具函数
"""
import os
import hashlib
import mimetypes
from typing import Optional, Tuple, List
import aiofiles
from pathlib import Path


def ensure_directory_exists(directory_path: str) -> bool:
    """
    确保目录存在，如果不存在则创建
    
    Args:
        directory_path: 目录路径
    
    Returns:
        bool: 是否成功创建或已存在
    """
    try:
        os.makedirs(directory_path, exist_ok=True)
        return True
    except Exception as e:
        print(f"创建目录失败: {e}")
        return False


def get_file_size(file_path: str) -> int:
    """
    获取文件大小（字节）
    
    Args:
        file_path: 文件路径
    
    Returns:
        int: 文件大小，如果文件不存在返回0
    """
    try:
        return os.path.getsize(file_path) if os.path.exists(file_path) else 0
    except Exception:
        return 0


def get_file_extension(filename: str) -> str:
    """
    获取文件扩展名
    
    Args:
        filename: 文件名
    
    Returns:
        str: 文件扩展名（包含点号）
    """
    return os.path.splitext(filename)[1].lower()


def get_filename_without_extension(filename: str) -> str:
    """
    获取不含扩展名的文件名
    
    Args:
        filename: 文件名
    
    Returns:
        str: 不含扩展名的文件名
    """
    return os.path.splitext(filename)[0]


def is_valid_model_format(filename: str) -> bool:
    """
    检查是否为有效的3D模型文件格式
    
    Args:
        filename: 文件名
    
    Returns:
        bool: 是否为有效格式
    """
    valid_extensions = {'.obj', '.glb', '.gltf', '.ply', '.fbx', '.dae', '.3ds', '.stl'}
    return get_file_extension(filename) in valid_extensions


def is_valid_image_format(filename: str) -> bool:
    """
    检查是否为有效的图片文件格式
    
    Args:
        filename: 文件名
    
    Returns:
        bool: 是否为有效格式
    """
    valid_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.tiff'}
    return get_file_extension(filename) in valid_extensions


async def calculate_file_hash(file_path: str, algorithm: str = 'md5') -> Optional[str]:
    """
    计算文件哈希值
    
    Args:
        file_path: 文件路径
        algorithm: 哈希算法 (md5, sha1, sha256)
    
    Returns:
        Optional[str]: 文件哈希值，失败时返回None
    """
    try:
        hash_func = getattr(hashlib, algorithm)()
        
        async with aiofiles.open(file_path, 'rb') as f:
            while chunk := await f.read(8192):
                hash_func.update(chunk)
        
        return hash_func.hexdigest()
    except Exception as e:
        print(f"计算文件哈希失败: {e}")
        return None


def get_mime_type(filename: str) -> str:
    """
    根据文件名获取MIME类型
    
    Args:
        filename: 文件名
    
    Returns:
        str: MIME类型
    """
    mime_type, _ = mimetypes.guess_type(filename)
    return mime_type or 'application/octet-stream'


def format_file_size(size_bytes: int) -> str:
    """
    格式化文件大小为可读字符串
    
    Args:
        size_bytes: 文件大小（字节）
    
    Returns:
        str: 格式化后的文件大小
    """
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    size = float(size_bytes)
    
    while size >= 1024.0 and i < len(size_names) - 1:
        size /= 1024.0
        i += 1
    
    return f"{size:.1f} {size_names[i]}"


def validate_filename(filename: str) -> Tuple[bool, Optional[str]]:
    """
    验证文件名是否合法
    
    Args:
        filename: 文件名
    
    Returns:
        Tuple[bool, Optional[str]]: (是否合法, 错误消息)
    """
    if not filename:
        return False, "文件名不能为空"
    
    if len(filename) > 255:
        return False, "文件名过长"
    
    # 检查非法字符
    invalid_chars = '<>:"|?*'
    for char in invalid_chars:
        if char in filename:
            return False, f"文件名包含非法字符: {char}"
    
    # 检查保留名称（Windows）
    reserved_names = {
        'CON', 'PRN', 'AUX', 'NUL',
        'COM1', 'COM2', 'COM3', 'COM4', 'COM5', 'COM6', 'COM7', 'COM8', 'COM9',
        'LPT1', 'LPT2', 'LPT3', 'LPT4', 'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9'
    }
    
    name_without_ext = get_filename_without_extension(filename).upper()
    if name_without_ext in reserved_names:
        return False, f"文件名是保留名称: {name_without_ext}"
    
    return True, None


async def copy_file(source_path: str, destination_path: str) -> bool:
    """
    异步复制文件
    
    Args:
        source_path: 源文件路径
        destination_path: 目标文件路径
    
    Returns:
        bool: 是否成功复制
    """
    try:
        # 确保目标目录存在
        destination_dir = os.path.dirname(destination_path)
        ensure_directory_exists(destination_dir)
        
        async with aiofiles.open(source_path, 'rb') as src:
            async with aiofiles.open(destination_path, 'wb') as dst:
                while chunk := await src.read(8192):
                    await dst.write(chunk)
        
        return True
    except Exception as e:
        print(f"复制文件失败: {e}")
        return False


async def move_file(source_path: str, destination_path: str) -> bool:
    """
    异步移动文件
    
    Args:
        source_path: 源文件路径
        destination_path: 目标文件路径
    
    Returns:
        bool: 是否成功移动
    """
    try:
        # 确保目标目录存在
        destination_dir = os.path.dirname(destination_path)
        ensure_directory_exists(destination_dir)
        
        # 尝试重命名（如果在同一文件系统）
        try:
            os.rename(source_path, destination_path)
            return True
        except OSError:
            # 跨文件系统移动，需要复制后删除
            if await copy_file(source_path, destination_path):
                os.remove(source_path)
                return True
            return False
    
    except Exception as e:
        print(f"移动文件失败: {e}")
        return False


def list_files_in_directory(
    directory_path: str,
    extension_filter: Optional[List[str]] = None,
    recursive: bool = False
) -> List[str]:
    """
    列出目录中的文件
    
    Args:
        directory_path: 目录路径
        extension_filter: 扩展名过滤器（如 ['.obj', '.glb']）
        recursive: 是否递归搜索子目录
    
    Returns:
        List[str]: 文件路径列表
    """
    files = []
    
    try:
        if recursive:
            for root, dirs, filenames in os.walk(directory_path):
                for filename in filenames:
                    file_path = os.path.join(root, filename)
                    
                    if extension_filter:
                        if get_file_extension(filename) in extension_filter:
                            files.append(file_path)
                    else:
                        files.append(file_path)
        else:
            for item in os.listdir(directory_path):
                item_path = os.path.join(directory_path, item)
                
                if os.path.isfile(item_path):
                    if extension_filter:
                        if get_file_extension(item) in extension_filter:
                            files.append(item_path)
                    else:
                        files.append(item_path)
    
    except Exception as e:
        print(f"列出目录文件失败: {e}")
    
    return files


def clean_filename(filename: str) -> str:
    """
    清理文件名，移除或替换非法字符
    
    Args:
        filename: 原始文件名
    
    Returns:
        str: 清理后的文件名
    """
    # 替换非法字符
    invalid_chars = '<>:"|?*'
    cleaned = filename
    
    for char in invalid_chars:
        cleaned = cleaned.replace(char, '_')
    
    # 移除连续的空格和下划线
    import re
    cleaned = re.sub(r'[_\s]+', '_', cleaned)
    
    # 移除开头和结尾的特殊字符
    cleaned = cleaned.strip('._- ')
    
    # 确保不为空
    if not cleaned:
        cleaned = 'unnamed_file'
    
    return cleaned


def get_directory_size(directory_path: str) -> int:
    """
    获取目录总大小（字节）
    
    Args:
        directory_path: 目录路径
    
    Returns:
        int: 目录总大小
    """
    total_size = 0
    
    try:
        for root, dirs, files in os.walk(directory_path):
            for file in files:
                file_path = os.path.join(root, file)
                total_size += get_file_size(file_path)
    except Exception as e:
        print(f"计算目录大小失败: {e}")
    
    return total_size


async def compress_file(file_path: str, compression_level: int = 6) -> Optional[str]:
    """
    压缩文件（使用gzip）
    
    Args:
        file_path: 文件路径
        compression_level: 压缩级别 (0-9)
    
    Returns:
        Optional[str]: 压缩文件路径，失败时返回None
    """
    import gzip
    
    try:
        compressed_path = f"{file_path}.gz"
        
        async with aiofiles.open(file_path, 'rb') as f_in:
            with gzip.open(compressed_path, 'wb', compresslevel=compression_level) as f_out:
                while chunk := await f_in.read(8192):
                    f_out.write(chunk)
        
        return compressed_path
    except Exception as e:
        print(f"压缩文件失败: {e}")
        return None


def create_safe_path(base_path: str, filename: str) -> str:
    """
    创建安全的文件路径，防止路径遍历攻击
    
    Args:
        base_path: 基础路径
        filename: 文件名
    
    Returns:
        str: 安全的文件路径
    """
    # 清理文件名
    safe_filename = clean_filename(filename)
    
    # 使用 Path 来安全地连接路径
    base = Path(base_path).resolve()
    file_path = (base / safe_filename).resolve()
    
    # 确保结果路径在基础路径内
    try:
        file_path.relative_to(base)
        return str(file_path)
    except ValueError:
        # 如果路径不在基础路径内，返回安全的默认路径
        return str(base / safe_filename)
