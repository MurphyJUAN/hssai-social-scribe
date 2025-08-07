# ================================
# 5. 統計 API 端點 - app/api/endpoints/analytics.py
# ================================

from datetime import datetime, date
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from core.database import get_db
from core.services.analytics_service import AnalyticsService
from typing import Optional

router = APIRouter()

@router.get("/traffic")
async def get_traffic_stats(
    start: str = Query(..., description="開始日期 YYYY-MM-DD"),
    end: str = Query(..., description="結束日期 YYYY-MM-DD"),
    db: Session = Depends(get_db)
):
    """獲取流量統計"""
    try:
        start_date = datetime.strptime(start, "%Y-%m-%d").date()
        end_date = datetime.strptime(end, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(status_code=400, detail="日期格式錯誤，請使用 YYYY-MM-DD")
    
    if start_date > end_date:
        raise HTTPException(status_code=400, detail="開始日期不能晚於結束日期")
    
    analytics = AnalyticsService(db)
    return analytics.get_traffic_stats(start_date, end_date)

@router.get("/errors")
async def get_recent_errors(
    limit: int = Query(50, ge=1, le=1000, description="返回記錄數量"),
    db: Session = Depends(get_db)
):
    """獲取最近的錯誤記錄"""
    analytics = AnalyticsService(db)
    return analytics.get_recent_errors(limit)

@router.get("/models")
async def get_model_usage(
    days: int = Query(30, ge=1, le=365, description="統計天數"),
    db: Session = Depends(get_db)
):
    """獲取模型使用統計"""
    analytics = AnalyticsService(db)
    return analytics.get_model_usage_stats(days)