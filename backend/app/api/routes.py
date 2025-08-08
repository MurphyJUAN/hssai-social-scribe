# ================================
# 10. app/api/routes.py - 路由定義
# ================================

from fastapi import APIRouter
from .endpoints import transcription, report, treatment_plan, analytics

api_router = APIRouter()

# 包含各個端點模塊
api_router.include_router(transcription.router, tags=["transcription"])
api_router.include_router(report.router, tags=["report"])
api_router.include_router(treatment_plan.router, tags=["treatment_plan"])
api_router.include_router(analytics.router, tags=["analytics"])  # 🔑 新增
# api_router.include_router(health.router, tags=["health"])