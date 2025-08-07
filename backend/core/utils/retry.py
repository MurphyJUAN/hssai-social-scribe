# ================================
# 4. core/utils/retry.py - 重試機制
# ================================

import asyncio
import logging
from typing import Callable, Any

logger = logging.getLogger(__name__)

async def simple_retry(
    func: Callable,
    *args,
    max_retries: int = 3,
    backoff_base: float = 2,
    **kwargs
) -> Any:
    """簡單的重試機制"""
    last_error = None
    
    for attempt in range(max_retries):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            last_error = e
            error_str = str(e)
            
            # 根據錯誤類型決定是否重試
            if "502" in error_str or "Bad Gateway" in error_str:
                if attempt < max_retries - 1:
                    wait_time = backoff_base ** attempt
                    logger.info(f"🔄 502 錯誤，{wait_time} 秒後重試...")
                    await asyncio.sleep(wait_time)
                    continue
            elif "413" in error_str or "too large" in error_str.lower():
                logger.error(f"💥 檔案過大，跳過重試")
                break
            elif "timeout" in error_str.lower():
                if attempt < max_retries - 1:
                    logger.info(f"⏰ 請求超時，重試...")
                    await asyncio.sleep(3)
                    continue
            
            # 其他錯誤，短暫等待後重試
            if attempt < max_retries - 1:
                await asyncio.sleep(1)
                continue
    
    # 所有重試都失敗
    raise last_error