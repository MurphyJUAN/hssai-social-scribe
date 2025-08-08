# ================================
# 15. core/report/generator.py - 報告生成器
# ================================

import logging
from typing import List, AsyncGenerator
from core.utils.sse import send_sse_data
from core.report.templates import PromptTemplateManager
from core.utils.text_converter import text_converter

logger = logging.getLogger(__name__)

class ReportGenerator:
    """報告生成器 - 支持繁體中文"""
    
    def __init__(self, claude_client):
        self.claude_client = claude_client
        self.template_manager = PromptTemplateManager()
    
    async def generate_report_streaming(
        self, 
        transcript: str, 
        social_worker_notes: str,
        selected_sections: List[str], 
        required_sections: List[str]
    ) -> AsyncGenerator[str, None]:
        """生成記錄流式輸出 - 繁體中文版本"""
        try:
            yield send_sse_data('progress', progress=10, message='準備生成記錄...')
            
            # 建構 prompt
            prompt = self.template_manager.build_report_prompt(
                transcript, social_worker_notes, selected_sections, required_sections
            )
            
            yield send_sse_data('progress', progress=20, message='正在生成記錄...')
            
            # 🔑 收集完整的生成內容
            full_report = ""
            current_progress = 30
            
            # 調用 Claude API
            with self.claude_client.messages.stream(
                model="claude-4-sonnet-20250514",
                max_tokens=4000,
                temperature=0.3,
                messages=[{"role": "user", "content": prompt}]
            ) as stream:
                
                for event in stream:
                    if event.type == "content_block_delta":
                        text_chunk = event.delta.text
                        full_report += text_chunk  # 🔑 收集完整內容
                        
                        # 仍然發送進度更新，但不發送文字塊
                        current_progress = min(85, current_progress + 0.5)
                        yield send_sse_data('progress', progress=current_progress, message='生成中...')
                        
                    elif event.type == "message_stop":
                        break
            
            # 🔑 轉換為繁體中文
            yield send_sse_data('progress', progress=90, message='轉換為繁體中文...')
            traditional_report = text_converter.to_traditional(full_report)
            logger.info(f"✅ 報告已轉換為繁體中文，共 {len(traditional_report)} 字")
            
            # 🔑 分段發送繁體中文內容
            yield send_sse_data('progress', progress=95, message='發送報告內容...')
            
            # 按段落分割並發送
            paragraphs = traditional_report.split('\n\n')
            for i, paragraph in enumerate(paragraphs):
                if paragraph.strip():
                    yield send_sse_data('chunk', 
                                      text=paragraph.strip() + '\n\n',
                                      progress=95 + (i / len(paragraphs)) * 5)
            
            yield send_sse_data('complete', progress=100, message='記錄生成完成')
                        
        except Exception as e:
            logger.error(f"記錄生成失敗: {str(e)}")
            yield send_sse_data('error', error=f'記錄生成失敗: {str(e)}')