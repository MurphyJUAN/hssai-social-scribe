# ================================
# 1. app/config.py - 配置管理
# ================================

import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    OPENCC_CONFIG = 's2twp.json'
    # API Keys
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    CLAUDE_API_KEY = os.getenv('CLAUDE_API_KEY')
    
    # File Processing Limits
    MAX_CHUNK_SIZE = 15 * 1024 * 1024  # 15MB
    MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB
    MAX_SEGMENT_MINUTES = 8
    MAX_CONCURRENT_TRANSCRIPTIONS = 2
    
    # Supported Formats
    SUPPORTED_FORMATS = {'mp3', 'mp4', 'm4a', 'wav', 'webm', 'ogg', 'flac', 'aac'}
    
    # App Settings
    APP_NAME = "Social Work Report Generator"
    APP_VERSION = "2.0.0"
    
    @classmethod
    def validate(cls):
        """驗證必要的配置"""
        if not cls.OPENAI_API_KEY:
            raise ValueError("Missing OPENAI_API_KEY")
        if not cls.CLAUDE_API_KEY:
            raise ValueError("Missing CLAUDE_API_KEY")