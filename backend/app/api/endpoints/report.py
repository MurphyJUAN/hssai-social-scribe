# ================================
# 12. app/api/endpoints/report.py - 報告生成端點
# ================================

import logging
from typing import List
from fastapi import APIRouter, Request, HTTPException, Depends
from fastapi.responses import StreamingResponse

from app.dependencies import get_claude_client
from core.utils.sse import send_sse_data
from core.report.generator import ReportGenerator
from core.utils.text_converter import text_converter

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/generate-report")
async def generate_report(
    request: Request,
    claude_client = Depends(get_claude_client)
):
    """生成記錄初稿 API"""
    try:
        data = await request.json()
        
        transcript = data.get('transcript', '').strip()
        if not transcript:
            raise HTTPException(status_code=400, detail="逐字稿內容不能為空")
        
        social_worker_notes = data.get('socialWorkerNotes', '').strip()
        selected_sections = data.get('selectedSections', [])
        required_sections = data.get('requiredSections', [])
        
        # 創建報告生成器
        generator = ReportGenerator(claude_client)
        
        async def generate_response():
            async for chunk in generator.generate_report_streaming(
                transcript, social_worker_notes, selected_sections, required_sections
            ):
                yield chunk
        
        return StreamingResponse(
            generate_response(),
            media_type='text/event-stream',
            headers={
                'Cache-Control': 'no-cache',
                'Connection': 'keep-alive',
                'Access-Control-Allow-Origin': '*',
            }
        )
        
    except Exception as e:
        logger.error(f"API 處理錯誤: {str(e)}")
        raise HTTPException(status_code=500, detail=f"伺服器錯誤: {str(e)}")