# ================================
# 14. core/report/templates.py - 報告模板管理
# ================================

import json
import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class PromptTemplateManager:
    """Prompt 模板管理器"""
    
    def __init__(self, template_file: str = "prompts/report_prompts.json"):
        self.template_file = template_file
        self._templates = None
    
    def load_templates(self) -> Dict[str, Any]:
        """載入 prompt 模板"""
        if self._templates is None:
            try:
                with open(self.template_file, 'r', encoding='utf-8') as f:
                    self._templates = json.load(f)
            except FileNotFoundError:
                logger.error(f"找不到 {self.template_file} 檔案")
                self._templates = self._get_default_templates()
            except json.JSONDecodeError:
                logger.error(f"{self.template_file} 格式錯誤")
                self._templates = self._get_default_templates()
        
        return self._templates
    
    def _get_default_templates(self) -> Dict[str, Any]:
        """獲取默認模板（當文件不存在時使用）"""
        return {
            "report_generation": {
                "base_template": """請根據以下逐字稿內容和社工補充說明，生成一份完整的社工記錄初稿。

請包含以下基本段落：
1. 案主基本資料概述
2. 問題陳述與評估
3. 服務目標
4. 處遇計畫
5. 後續追蹤建議

{input}

請以專業的社工用語撰寫，內容要客觀、具體且有建設性。""",
                "optional_sections": {
                    "family_assessment": {
                        "title": "家庭評估",
                        "content": "請特別關注家庭結構、互動關係和支持系統。"
                    },
                    "risk_assessment": {
                        "title": "風險評估", 
                        "content": "請評估案主可能面臨的風險因子和保護因子。"
                    },
                    "resource_assessment": {
                        "title": "資源評估",
                        "content": "請評估案主現有資源和所需資源。"
                    }
                }
            }
        }
    
    def build_report_prompt(self, transcript: str, social_worker_notes: str, 
                          selected_sections: List[str], required_sections: List[str]) -> str:
        """建構記錄生成的 prompt"""
        templates = self.load_templates()
        
        # 基本模板
        base_template = templates['report_generation']['base_template']
        
        # 可選段落的額外指示
        optional_instructions = templates['report_generation']['optional_sections']
        
        # 建構額外指示文字
        additional_instructions = []
        
        for section in selected_sections:
            if section in optional_instructions:
                instruction = optional_instructions[section]
                additional_instructions.append(f"\n{instruction['title']}\n{instruction['content']}")
        
        # 組合完整的 prompt
        full_prompt = base_template
        
        if additional_instructions:
            full_prompt += "\n\n額外評估項目：" + "".join(additional_instructions)
        
        # 加入逐字稿和社工補充說明
        input_content = f"逐字稿內容：\n{transcript}"
        if social_worker_notes and social_worker_notes.strip():
            input_content += f"\n\n以下是社工對本案的補充說明，如果內容和前面訪視的逐字稿沒有衝突，就在訪視記錄中補充社工提到的內容；如果和逐字稿有衝突，則以社工的補充說明為準，並以社工的補充說明來更正逐字稿中提到的內容：\n{social_worker_notes}"
        
        # 替換 input 變數
        full_prompt = full_prompt.replace('{input}', input_content)

        print('>>fullPrompt:', full_prompt)
        
        return full_prompt