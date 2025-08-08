# ================================
# 3. 中間件 - core/middleware/logging_middleware.py
# ================================

import time
import json
import ipaddress
from fastapi import Request
from sqlalchemy.exc import SQLAlchemyError
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from models.api_usage_log import ApiUsageLog
from core.database import get_db_context
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class ApiLoggingMiddleware(BaseHTTPMiddleware):
    """API 使用記錄中間件"""
    
    def __init__(self, app):
        super().__init__(app)
        self.excluded_paths = {
            '/docs',
            '/redoc', 
            '/openapi.json',
            '/favicon.ico',
            '/health',  # 健康檢查不記錄
        }
        self.excluded_prefixes = ('/assets/', '/static/', '/css/', '/js/')
    
    def should_log(self, path: str) -> bool:
        """判斷是否需要記錄此請求"""
        if path in self.excluded_paths:
            return False
        
        if any(path.startswith(prefix) for prefix in self.excluded_prefixes):
            return False
            
        return True
    
    def get_client_ip(self, request: Request) -> str:
        """獲取客戶端真實IP"""
        # 檢查各種可能的 IP 頭
        possible_headers = [
            'x-forwarded-for',
            'x-real-ip', 
            'x-client-ip',
            'cf-connecting-ip'  # Cloudflare
        ]
        
        for header in possible_headers:
            ip_str = request.headers.get(header)
            if ip_str:
                # X-Forwarded-For 可能包含多個 IP，取第一個
                candidate = ip_str.split(',')[0].strip()
                if self.validate_ip(candidate):
                    return candidate
        
        # 如果沒有找到，使用 client.host
        return request.client.host if request.client else "unknown"
    
    def validate_ip(self, ip_str: str) -> bool:
        """驗證 IP 地址格式"""
        try:
            ipaddress.ip_address(ip_str)
            return True
        except ValueError:
            return False
    
    def extract_model_info(self, path: str, request_data: dict = None) -> str:
        """從請求中提取模型信息"""
        if path == '/backend/transcribe':
            return 'whisper-1'
        elif path == '/backend/generate-report':
            return 'claude-3-sonnet'
        elif path == '/backend/generate-treatment-plan':
            return 'claude-3-sonnet'
        return None
    
    def get_file_size(self, request: Request) -> int:
        """獲取上傳文件大小"""
        content_length = request.headers.get('content-length')
        if content_length:
            try:
                return int(content_length)
            except ValueError:
                pass
        return None
    
    async def dispatch(self, request: Request, call_next) -> Response:
        """處理請求並記錄"""
        path = request.url.path

        
        if not self.should_log(path):
            return await call_next(request)
        
        
        # 記錄開始時間
        start_time = time.time()
        
        # 獲取請求信息
        ip = self.get_client_ip(request)
        user_agent = request.headers.get('user-agent', '')
        method = request.method
        file_size = self.get_file_size(request)
        
        # 嘗試獲取請求數據（非文件上傳）
        request_data = None
        if method == 'POST' and 'multipart/form-data' not in request.headers.get('content-type', ''):
            try:
                # 對於 JSON 請求，嘗試解析
                body = await request.body()
                if body:
                    request_data = json.loads(body.decode())
            except Exception:
                # 解析失敗就忽略
                pass
        
        # 提取模型信息
        model_used = self.extract_model_info(path, request_data)
        
        # 處理請求
        success = 'success'
        error_message = None
        
        try:
            response = await call_next(request)
            
            # 根據狀態碼判斷是否成功
            if response.status_code >= 400:
                success = 'error'
                error_message = f"HTTP {response.status_code}"
                
        except Exception as e:
            success = 'error'
            error_message = str(e)
            # 重新拋出異常
            raise
        
        # 計算處理時間
        processing_time = int((time.time() - start_time) * 1000)  # 毫秒
        
        # 異步記錄到數據庫
        try:
            await self.log_to_database(
                timestamp=datetime.fromtimestamp(time.time()),
                ip=ip,
                endpoint=path,
                method=method,
                model_used=model_used,
                file_size=file_size,
                processing_time=processing_time,
                success=success,
                error_message=error_message,
                data_payload=request_data,
                user_agent=user_agent
            )
        except Exception as log_error:
            logger.error(f"記錄 API 使用失敗: {log_error}")
        
        return response
    
    async def log_to_database(self, **kwargs):
        """異步記錄到數據庫"""
        try:
            with get_db_context() as db:
                log_entry = ApiUsageLog(**kwargs)
                db.add(log_entry)
                # commit 在 context manager 中自動處理
        except SQLAlchemyError as e:
            logger.error(f"數據庫記錄錯誤: {e}")
        except Exception as e:
            logger.error(f"記錄 API 使用時發生未知錯誤: {e}")
