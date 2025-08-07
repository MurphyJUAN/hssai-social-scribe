# ================================
# 3. core/utils/sse.py - SSE 工具
# ================================

import json
import time
import logging

logger = logging.getLogger(__name__)

def send_sse_data(data_type: str, **kwargs) -> str:
    """發送標準的 SSE 格式資料"""
    data = {
        'type': data_type,
        'timestamp': time.time(),
        **kwargs
    }
    
    try:
        json_str = json.dumps(data, ensure_ascii=False, separators=(',', ':'))
        sse_message = f"data: {json_str}\n\n"
        
        if data_type in ['progress', 'complete', 'error']:
            logger.debug(f"📤 發送 SSE: {data_type} - {data.get('progress', 0)}% - {data.get('message', '')}")
        
        return sse_message
        
    except Exception as e:
        logger.error(f"❌ SSE 數據序列化失敗: {e}")
        error_data = {
            'type': 'error',
            'error': f'服務器內部錯誤: {str(e)}',
            'timestamp': time.time()
        }
        return f"data: {json.dumps(error_data)}\n\n"