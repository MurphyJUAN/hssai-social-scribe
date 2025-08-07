# ================================
# 1. 數據庫模型 - models/api_usage_log.py
# ================================

from sqlalchemy import Column, Integer, String, DateTime, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from datetime import datetime

Base = declarative_base()

class ApiUsageLog(Base):
    __tablename__ = 'api_usage_logs'
    __table_args__ = {'schema': 'social_work'}  # 可以改成您想要的 schema

    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, nullable=False, default=func.now())
    ip = Column(String(45), nullable=False)
    endpoint = Column(String(255), nullable=False)
    method = Column(String(10), nullable=False)  # GET, POST, etc.
    model_used = Column(String(50))  # whisper-1, claude-3-sonnet, etc.
    file_size = Column(Integer)  # 文件大小（bytes）
    processing_time = Column(Integer)  # 處理時間（毫秒）
    success = Column(String(10), nullable=False)  # success, error
    error_message = Column(Text)  # 錯誤訊息
    data_payload = Column(JSON)  # 請求數據
    user_agent = Column(Text)
    
    def __repr__(self):
        return f"<ApiUsageLog(id={self.id}, endpoint={self.endpoint}, ip={self.ip})>"