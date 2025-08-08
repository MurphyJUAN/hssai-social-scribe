# ================================
# 15. core/treatmentplan/generator.py - 處遇計畫生成器
# ================================

import logging
from typing import List, AsyncGenerator
from core.utils.sse import send_sse_data
from core.treatmentplan.templates import PromptTemplateManager
from core.utils.text_converter import text_converter

logger = logging.getLogger(__name__)

class TreatmentPlanGenerator:
    """報告生成器"""
    
    def __init__(self, claude_client):
        self.claude_client = claude_client
        self.template_manager = PromptTemplateManager()
    
    async def generate_treatment_plan_streaming(
        self, 
        report: str,
        selected_service_domains: List[str], 
    ) -> AsyncGenerator[str, None]:
        """生成記錄流式輸出"""
        try:
            yield send_sse_data('progress', progress=10, message='準備生成處遇計畫...')
            
            # 建構 prompt
            prompt = self.template_manager.build_plan_prompt(
                report, selected_service_domains
            )
            
            yield send_sse_data('progress', progress=20, message='正在生成處遇計畫...')
            
            # 🔑 收集完整內容
            full_plan = ""
            current_progress = 30
            
            with self.claude_client.messages.stream(
                model="claude-4-sonnet-20250514",
                max_tokens=4000,
                temperature=0.3,
                messages=[{"role": "user", "content": prompt}]
            ) as stream:
                
                for event in stream:
                    if event.type == "content_block_delta":
                        text_chunk = event.delta.text
                        full_plan += text_chunk
                        
                        current_progress = min(85, current_progress + 0.5)
                        yield send_sse_data('progress', progress=current_progress, message='生成中...')
                        
                    elif event.type == "message_stop":
                        break
            
            # 🔑 轉換為繁體中文
            yield send_sse_data('progress', progress=90, message='轉換為繁體中文...')
            traditional_plan = text_converter.to_traditional(full_plan)
            logger.info(f"✅ 處遇計畫已轉換為繁體中文，共 {len(traditional_plan)} 字")
            
            # 分段發送
            yield send_sse_data('progress', progress=95, message='發送處遇計畫...')
            
            paragraphs = traditional_plan.split('\n\n')
            for i, paragraph in enumerate(paragraphs):
                if paragraph.strip():
                    yield send_sse_data('chunk', 
                                      text=paragraph.strip() + '\n\n',
                                      progress=95 + (i / len(paragraphs)) * 5)
            
            yield send_sse_data('complete', progress=100, message='處遇計畫生成完成')
            
        except Exception as e:
            logger.error(f"處遇計畫生成失敗: {str(e)}")
            yield send_sse_data('error', error=f'處遇計畫生成失敗: {str(e)}')