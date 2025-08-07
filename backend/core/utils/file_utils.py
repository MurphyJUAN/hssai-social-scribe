# ================================
# 5. core/utils/file_utils.py - 文件工具
# ================================

import os
import tempfile
import aiofiles
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

async def save_upload_file(upload_file, suffix: str = None) -> str:
    """保存上傳文件到臨時位置 - 修復版本"""
    # 🔑 重置文件指針到開始位置
    await upload_file.seek(0)
    content = await upload_file.read()
    
    if len(content) == 0:
        raise ValueError("上傳的文件為空")
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_file:
        tmp_file.write(content)
        temp_file_path = tmp_file.name
    
    logger.info(f"💾 文件已保存到: {temp_file_path}")
    return temp_file_path

def cleanup_files(file_paths: list):
    """清理臨時文件"""
    for file_path in file_paths:
        try:
            if file_path and os.path.exists(file_path):
                os.unlink(file_path)
                logger.info(f"🗑️ 已刪除: {os.path.basename(file_path)}")
        except Exception as e:
            logger.warning(f"清理失敗 {file_path}: {e}")

def validate_audio_file(filename: str, file_size: int, supported_formats: set, max_size: int):
    """驗證音頻文件"""
    if not filename:
        raise ValueError("沒有提供檔案名稱")
    
    file_extension = filename.split('.')[-1].lower()
    if file_extension not in supported_formats:
        raise ValueError(f"不支援的檔案格式。支援格式: {', '.join(supported_formats)}")
    
    if file_size > max_size:
        raise ValueError(f"檔案大小超過限制 ({max_size // (1024*1024)}MB)")
    
    if file_size == 0:
        raise ValueError("上傳的文件為空")