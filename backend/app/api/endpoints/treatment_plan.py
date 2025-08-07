# ================================
# 12. app/api/endpoints/treatment_plane.py - 處遇計畫生成端點
# ================================

import logging
from typing import List
from fastapi import APIRouter, Request, HTTPException, Depends
from fastapi.responses import StreamingResponse

from app.dependencies import get_claude_client
from core.utils.sse import send_sse_data
from core.treatmentplan.generator import TreatmentPlanGenerator

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/generate-treatment-plan")
async def generate_treatment_plan(
    request: Request,
    claude_client = Depends(get_claude_client)
):
    """生成記錄初稿 API"""
    try:
        data = await request.json()
        
        report = data.get('reportDraft', '').strip()
        if not report:
            raise HTTPException(status_code=400, detail="記錄初稿內容不能為空")
        
        selected_service_domains = data.get('selectedServiceDomains', [])
        
        # 創建報告生成器
        generator = TreatmentPlanGenerator(claude_client)
        
        async def generate_response():
            async for chunk in generator.generate_treatment_plan_streaming(
                report, selected_service_domains
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