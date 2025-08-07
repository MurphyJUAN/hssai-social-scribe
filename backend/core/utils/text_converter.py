# ================================
# 2. core/utils/text_converter.py - 文字轉換工具
# ================================

import opencc
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class TextConverter:
    """文字轉換工具類"""
    
    def __init__(self):
        self._converter = None
        self._initialized = False
    
    def _initialize_converter(self) -> bool:
        """初始化 OpenCC 轉換器"""
        if self._initialized:
            return self._converter is not None
        
        try:
            # 使用簡體轉繁體（台灣標準）配置
            self._converter = opencc.OpenCC('s2twp.json')
            logger.info("✅ OpenCC 繁體字轉換器初始化成功")
            self._initialized = True
            return True
        except Exception as e:
            logger.error(f"❌ OpenCC 初始化失敗: {e}")
            self._converter = None
            self._initialized = True
            return False
    
    def to_traditional(self, text: str) -> str:
        """
        將文字轉換為繁體中文（台灣標準）
        
        Args:
            text: 輸入文字
            
        Returns:
            轉換後的繁體中文文字，如果轉換失敗則返回原文字
        """
        if not text or not text.strip():
            return text
        
        try:
            # 確保轉換器已初始化
            if not self._initialize_converter():
                logger.warning("OpenCC 轉換器未初始化，返回原文字")
                return text
            
            # 執行轉換
            converted_text = self._converter.convert(text)
            
            if converted_text != text:
                logger.info(f"🔄 文字轉換: {len(text)} 字 -> {len(converted_text)} 字")
            
            return converted_text
            
        except Exception as e:
            logger.error(f"❌ 文字轉換失敗: {e}")
            return text  # 失敗時返回原文字
    
    def convert_with_stats(self, text: str) -> dict:
        """
        轉換文字並返回統計信息
        
        Returns:
            {
                'original_text': str,
                'converted_text': str,
                'original_length': int,
                'converted_length': int,
                'changed': bool,
                'success': bool
            }
        """
        original_text = text
        converted_text = self.to_traditional(text)
        
        return {
            'original_text': original_text,
            'converted_text': converted_text,
            'original_length': len(original_text),
            'converted_length': len(converted_text),
            'changed': original_text != converted_text,
            'success': self._converter is not None
        }

# 創建全局實例
text_converter = TextConverter()