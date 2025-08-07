# ================================
# 2. app/dependencies.py - 依賴注入
# ================================

from openai import AsyncOpenAI
import anthropic
from .config import Config

# 驗證配置
Config.validate()

# 創建 API 客戶端
openai_client = AsyncOpenAI(api_key=Config.OPENAI_API_KEY)
claude_client = anthropic.Anthropic(api_key=Config.CLAUDE_API_KEY)

def get_openai_client():
    return openai_client

def get_claude_client():
    return claude_client