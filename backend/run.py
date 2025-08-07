# run.py
import uvicorn
from app.main import app

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",  # 🔑 關鍵：使用字符串路徑
        host="0.0.0.0",
        port=5174,
        reload=True,
        log_level="info",
        access_log=True
    )
