# ================================
# 9. core/audio/transcriber.py - 轉錄服務
# ================================

import io
import os
import asyncio
import aiofiles
import logging
from typing import Tuple
from core.utils.retry import simple_retry
from core.audio.processor import AudioProcessor

logger = logging.getLogger(__name__)

class AudioTranscriber:
    """音頻轉錄服務"""
    
    def __init__(self, openai_client):
        self.openai_client = openai_client
    
    async def transcribe_chunk(self, chunk_path: str, chunk_index: int) -> Tuple[int, str, str]:
        """轉錄單個音頻分段"""
        try:
            logger.info(f"🎯 轉換分段 {chunk_index}: {chunk_path}")
            
            if not os.path.exists(chunk_path):
                raise FileNotFoundError(f"分段文件不存在: {chunk_path}")
            
            file_size = os.path.getsize(chunk_path)
            logger.info(f"📏 分段 {chunk_index} 大小: {file_size / 1024 / 1024:.2f}MB")
            
            # 如果文件太大，嘗試額外壓縮
            processing_path = chunk_path
            if file_size > 8 * 1024 * 1024:  # 8MB
                logger.warning(f"⚠️ 分段 {chunk_index} 過大，嘗試額外壓縮...")
                extra_compressed_path = f"{chunk_path}_extra_compressed.mp3"
                
                success = await AudioProcessor.compress_audio(chunk_path, extra_compressed_path, aggressive=True)
                if success and os.path.exists(extra_compressed_path):
                    new_size = os.path.getsize(extra_compressed_path)
                    if new_size < file_size and new_size > 0:
                        processing_path = extra_compressed_path
                        logger.info(f"✅ 額外壓縮成功: {new_size / 1024 / 1024:.2f}MB")
            
            # 讀取並發送到 OpenAI
            async with aiofiles.open(processing_path, 'rb') as audio_file:
                audio_data = await audio_file.read()
                
                if not audio_data:
                    raise ValueError(f"分段文件為空: {processing_path}")
                
                audio_io = io.BytesIO(audio_data)
                audio_io.name = f"chunk_{chunk_index}.mp3"
                
                logger.info(f"📡 發送分段 {chunk_index} 到 OpenAI...")
                
                response = await self.openai_client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_io,
                    response_format="verbose_json",
                    language="zh",
                    timeout=120.0
                )
                
                text = response.text
                logger.info(f"✅ 分段 {chunk_index} 轉換成功，文字長度: {len(text)}")
                
                # 清理額外壓縮文件
                if processing_path != chunk_path:
                    try:
                        os.unlink(processing_path)
                    except:
                        pass
                
                return chunk_index, text, None
                
        except Exception as e:
            error_str = str(e)
            logger.error(f"❌ 分段 {chunk_index} 轉換失敗: {error_str}")
            
            # 判斷錯誤類型
            if "413" in error_str or "too large" in error_str.lower():
                return chunk_index, "[檔案過大，無法處理]", f"檔案過大: {error_str}"
            
            return chunk_index, "", error_str
    
    async def transcribe_chunk_with_retry(self, chunk_path: str, chunk_index: int, max_retries: int = 3) -> Tuple[int, str, str]:
        """帶重試機制的轉錄"""
        try:
            return await simple_retry(
                self.transcribe_chunk,
                chunk_path,
                chunk_index,
                max_retries=max_retries
            )
        except Exception as e:
            error_msg = f"分段 {chunk_index} 所有重試都失敗: {str(e)}"
            logger.error(error_msg)
            return chunk_index, "", error_msg