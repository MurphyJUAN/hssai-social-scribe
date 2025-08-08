# ================================
# 6. app/main.py - 主應用入口
# ================================

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import logging
import os
from .config import Config
from .api.routes import api_router
from core.middleware.logging_middleware import ApiLoggingMiddleware
from core.database import create_tables

# 設置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title=Config.APP_NAME,
    description="AI-powered social work report generation service with analytics",
    version=Config.APP_VERSION
)

# 🔑 添加 API 記錄中間件
app.add_middleware(ApiLoggingMiddleware)

# 添加 CORS 中間件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 包含 API 路由
app.include_router(api_router, prefix="/backend")

frontend_dist_path = os.path.join(os.path.dirname(__file__), "..", "..", "dist")

app.mount("/assets", StaticFiles(directory=os.path.join(frontend_dist_path, "assets")), name="assets")


# 🔑 在啟動時創建數據庫表
@app.on_event("startup")
async def startup_event():
    create_tables()
    logger.info("📊 API 記錄系統已啟用")

# 根路徑 "/" 直接回傳 index.html
@app.get("/")
async def serve_frontend():
    return FileResponse(os.path.join(frontend_dist_path, "index.html"))

# 如果要支援 Vue/React SPA 的前端路由，例如 /about、/dashboard
@app.get("/{full_path:path}")
async def serve_spa(full_path: str):
    file_path = os.path.join(frontend_dist_path, full_path)
    if os.path.exists(file_path):
        return FileResponse(file_path)
    return FileResponse(os.path.join(frontend_dist_path, "index.html"))

if __name__ == "__main__":
    import uvicorn
    
    logger.info(f"🚀 啟動 {Config.APP_NAME}...")
    logger.info(f"✅ OpenAI API 金鑰已載入")
    logger.info(f"✅ Claude API 金鑰已載入")
    logger.info(f"📊 數據庫記錄已啟用")
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0", 
        port=5174,
        reload=True,
        log_level="info",
        access_log=True
    )