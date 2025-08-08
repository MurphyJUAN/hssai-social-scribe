# ================================
# 4. 統計查詢服務 - core/services/analytics_service.py
# ================================

from datetime import datetime, timedelta, date
from sqlalchemy.orm import Session
from sqlalchemy import func, case
from models.api_usage_log import ApiUsageLog
from typing import List, Dict, Any

class AnalyticsService:
    """API 使用分析服務"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_traffic_stats(self, start_date: date, end_date: date) -> List[Dict[str, Any]]:
        """獲取指定日期範圍的流量統計"""
        
        # 查詢數據
        rows = self.db.query(
            func.date(ApiUsageLog.timestamp).label('day'),
            func.count().label('total_requests'),
            func.count(func.distinct(ApiUsageLog.ip)).label('distinct_ips'),
            func.sum(
                case(
                    (ApiUsageLog.endpoint == '/backend/transcribe', 1),
                    else_=0
                )
            ).label('transcribe_count'),
            func.sum(
                case(
                    (ApiUsageLog.endpoint == '/backend/generate-report', 1),
                    else_=0
                )
            ).label('report_count'),
            func.sum(
                case(
                    (ApiUsageLog.endpoint == '/backend/generate-treatment-plan', 1),
                    else_=0
                )
            ).label('treatment_count'),
            func.sum(
                case(
                    (ApiUsageLog.success == 'error', 1),
                    else_=0
                )
            ).label('error_count'),
            func.avg(ApiUsageLog.processing_time).label('avg_processing_time'),
            func.sum(ApiUsageLog.file_size).label('total_file_size')
        ).filter(
            func.date(ApiUsageLog.timestamp) >= start_date,
            func.date(ApiUsageLog.timestamp) <= end_date
        ).group_by(
            func.date(ApiUsageLog.timestamp)
        ).order_by(
            func.date(ApiUsageLog.timestamp)
        ).all()
        
        # 建立數據映射
        data_map = {}
        for row in rows:
            data_map[row.day] = {
                "total_requests": row.total_requests or 0,
                "distinct_ips": row.distinct_ips or 0,
                "transcribe_count": row.transcribe_count or 0,
                "report_count": row.report_count or 0,
                "treatment_count": row.treatment_count or 0,
                "error_count": row.error_count or 0,
                "success_rate": round(
                    ((row.total_requests - (row.error_count or 0)) / row.total_requests * 100) 
                    if row.total_requests > 0 else 0, 2
                ),
                "avg_processing_time": round(row.avg_processing_time or 0, 2),
                "total_file_size": row.total_file_size or 0
            }

        
        # 填充缺失的日期
        result = []
        current_day = start_date
        while current_day <= end_date:
            if current_day in data_map:
                stats = data_map[current_day]
            else:
                stats = {
                    "total_requests": 0,
                    "distinct_ips": 0,
                    "transcribe_count": 0,
                    "report_count": 0,
                    "treatment_count": 0,
                    "error_count": 0,
                    "success_rate": 0,
                    "avg_processing_time": 0,
                    "total_file_size": 0
                }
            
            result.append({
                "date": current_day.strftime("%Y-%m-%d"),
                **stats
            })
            current_day += timedelta(days=1)
        
        return result
    
    def get_recent_errors(self, limit: int = 50) -> List[Dict[str, Any]]:
        """獲取最近的錯誤記錄"""
        errors = self.db.query(ApiUsageLog).filter(
            ApiUsageLog.success == 'error'
        ).order_by(
            ApiUsageLog.timestamp.desc()
        ).limit(limit).all()
        
        return [
            {
                "timestamp": error.timestamp.isoformat(),
                "ip": error.ip,
                "endpoint": error.endpoint,
                "method": error.method,
                "error_message": error.error_message,
                "processing_time": error.processing_time
            }
            for error in errors
        ]
    
    def get_model_usage_stats(self, days: int = 30) -> Dict[str, Any]:
        """獲取模型使用統計"""
        start_date = datetime.now() - timedelta(days=days)
        
        stats = self.db.query(
            ApiUsageLog.model_used,
            func.count().label('usage_count'),
            func.avg(ApiUsageLog.processing_time).label('avg_time')
        ).filter(
            ApiUsageLog.timestamp >= start_date,
            ApiUsageLog.model_used.isnot(None)
        ).group_by(
            ApiUsageLog.model_used
        ).all()
        
        return {
            stat.model_used: {
                "usage_count": stat.usage_count,
                "avg_processing_time": round(stat.avg_time or 0, 2)
            }
            for stat in stats
        }