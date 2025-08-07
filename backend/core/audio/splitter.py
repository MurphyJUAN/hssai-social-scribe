# ================================
# 8. core/audio/splitter.py - 音頻分割器
# ================================

import os
import math
import asyncio
import concurrent.futures
import logging
from typing import List
from pydub import AudioSegment

logger = logging.getLogger(__name__)

class AudioSplitter:
    """音頻分割器"""
    
    @staticmethod
    def should_split_by_duration(duration_minutes: float, file_size_mb: float) -> bool:
        """判斷是否需要按時長分割"""
        if duration_minutes > 15:  # 強制分割
            return True
        elif duration_minutes > 10:  # 建議分割
            return True
        elif duration_minutes > 5 and file_size_mb > 5:  # 條件分割
            return True
        return False
    
    @staticmethod
    async def smart_split_by_duration(file_path: str, duration_minutes: float, max_segment_minutes: int = 8) -> List[str]:
        """智能分割音頻 - 按時長分割"""
        try:
            logger.info(f"🎯 智能分割音頻: {file_path}, 總時長: {duration_minutes:.1f} 分鐘")
            
            # 如果不需要分割
            if not AudioSplitter.should_split_by_duration(duration_minutes, os.path.getsize(file_path) / 1024 / 1024):
                logger.info("✅ 音頻時長適中，無需分割")
                return [file_path]
            
            # 計算分段數量
            num_segments = math.ceil(duration_minutes / max_segment_minutes)
            
            logger.info(f"📊 將分割為 {num_segments} 段，每段約 {max_segment_minutes} 分鐘")
            
            def split_sync():
                audio = AudioSegment.from_file(file_path)
                total_duration_ms = len(audio)
                segment_duration_ms = total_duration_ms / num_segments
                
                segments = []
                for i in range(num_segments):
                    start_ms = int(i * segment_duration_ms)
                    end_ms = int((i + 1) * segment_duration_ms) if i < num_segments - 1 else total_duration_ms
                    
                    segment = audio[start_ms:end_ms]
                    
                    segment_path = f"{file_path}_time_segment_{i:02d}.mp3"
                    segment.export(
                        segment_path,
                        format="mp3",
                        bitrate="64k",
                        parameters=["-ar", "16000", "-ac", "1"]
                    )
                    
                    segments.append(segment_path)
                    segment_size = os.path.getsize(segment_path) / 1024 / 1024
                    segment_duration = len(segment) / 1000 / 60
                    
                    logger.info(f"✅ 分段 {i}: {segment_duration:.1f} 分鐘, {segment_size:.1f}MB")
                
                return segments
            
            loop = asyncio.get_event_loop()
            with concurrent.futures.ThreadPoolExecutor() as executor:
                segments = await loop.run_in_executor(executor, split_sync)
            
            logger.info(f"🎉 智能分割完成，生成 {len(segments)} 個分段")
            return segments
            
        except Exception as e:
            logger.error(f"❌ 智能分割失敗: {e}")
            return [file_path]

    @staticmethod
    def _split_by_size_sync(file_path: str, max_size: int) -> List[str]:
        """同步按文件大小分割音頻"""
        try:
            logger.info(f"開始按大小分割音頻: {file_path}, 最大大小: {max_size / 1024 / 1024:.1f}MB")
            
            audio = AudioSegment.from_file(file_path)
            file_size = os.path.getsize(file_path)
            
            if file_size <= max_size:
                logger.info("檔案小於限制，無需分割")
                return [file_path]
            
            num_chunks = math.ceil(file_size / max_size)
            duration_per_chunk = len(audio) // num_chunks
            
            chunks = []
            for i in range(num_chunks):
                start_time = i * duration_per_chunk
                end_time = start_time + duration_per_chunk if i < num_chunks - 1 else len(audio)
                
                chunk = audio[start_time:end_time]
                chunk_path = f"{file_path}_chunk_{i}.mp3"
                chunk.export(
                    chunk_path, 
                    format="mp3", 
                    bitrate="64k",
                    parameters=["-q:a", "5"]
                )
                chunks.append(chunk_path)
                
                logger.info(f"分段 {i} 已保存: {chunk_path}")
            
            return chunks
            
        except Exception as e:
            logger.error(f"按大小分割失敗: {str(e)}", exc_info=True)
            return [file_path]

    @staticmethod
    async def split_by_size(file_path: str, max_size: int) -> List[str]:
        """異步按文件大小分割音頻"""
        try:
            loop = asyncio.get_event_loop()
            with concurrent.futures.ThreadPoolExecutor() as executor:
                result = await loop.run_in_executor(
                    executor,
                    AudioSplitter._split_by_size_sync,
                    file_path,
                    max_size
                )
            return result
        except Exception as e:
            logger.error(f"異步分割音頻失敗: {str(e)}")
            return [file_path]