# ================================
# 7. core/audio/processor.py - 音頻處理核心
# ================================

import os
import math
import asyncio
import concurrent.futures
import logging
from typing import Dict, Any, List
from pydub import AudioSegment
from pydub.effects import normalize
import json
import subprocess

logger = logging.getLogger(__name__)

class AudioProcessor:
    """音頻處理器 - 負責音頻信息獲取和壓縮"""
    
    @staticmethod
    def _get_audio_info_sync(file_path: str) -> Dict[str, Any]:
        """同步獲取音頻文件信息"""
        try:
            audio = AudioSegment.from_file(file_path)
            return {
                'duration_ms': len(audio),
                'duration_min': len(audio) / 1000 / 60,
                'channels': audio.channels,
                'frame_rate': audio.frame_rate,
                'sample_width': audio.sample_width
            }
        except Exception as e:
            logger.error(f"pydub 獲取音頻信息失敗: {str(e)}")
            return AudioProcessor._get_audio_info_with_ffprobe(file_path)
    
    @staticmethod
    def _get_audio_info_with_ffprobe(file_path: str) -> Dict[str, Any]:
        """使用 ffprobe 獲取音頻信息（備選方案）"""
        try:
            result = subprocess.run([
                'ffprobe', '-v', 'quiet', '-print_format', 'json',
                '-show_format', '-show_streams', file_path
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                info = json.loads(result.stdout)
                duration = float(info.get('format', {}).get('duration', 0))
                streams = info.get('streams', [])
                audio_stream = next((s for s in streams if s.get('codec_type') == 'audio'), {})
                
                return {
                    'duration_ms': duration * 1000,
                    'duration_min': duration / 60,
                    'channels': int(audio_stream.get('channels', 1)),
                    'frame_rate': int(audio_stream.get('sample_rate', 44100)),
                    'sample_width': 2
                }
        except Exception as e:
            logger.error(f"ffprobe 獲取音頻信息失敗: {e}")
        
        return {}
    
    @staticmethod
    async def get_audio_info(file_path: str) -> Dict[str, Any]:
        """異步獲取音頻文件信息"""
        try:
            loop = asyncio.get_event_loop()
            with concurrent.futures.ThreadPoolExecutor() as executor:
                result = await loop.run_in_executor(
                    executor, 
                    AudioProcessor._get_audio_info_sync, 
                    file_path
                )
            return result
        except Exception as e:
            logger.error(f"獲取音頻信息失敗: {str(e)}")
            return {}

    @staticmethod
    def _compress_audio_sync(input_path: str, output_path: str, aggressive: bool = False) -> bool:
        """同步壓縮音頻文件"""
        try:
            logger.info(f"開始{'激進' if aggressive else '標準'}壓縮: {input_path}")
            
            audio = AudioSegment.from_file(input_path)
            logger.info(f"原始音頻: {len(audio)}ms, {audio.channels}聲道, {audio.frame_rate}Hz")
            
            if aggressive:
                # 激進壓縮設置
                audio = audio.set_frame_rate(12000)
                audio = audio.set_channels(1)
                audio = normalize(audio)
                
                audio.export(
                    output_path,
                    format="mp3",
                    bitrate="32k",
                    parameters=["-q:a", "9"]
                )
            else:
                # 標準壓縮設置
                if audio.frame_rate > 16000:
                    audio = audio.set_frame_rate(16000)
                if audio.channels > 1:
                    audio = audio.set_channels(1)
                audio = normalize(audio)
                
                audio.export(
                    output_path,
                    format="mp3",
                    bitrate="64k",
                    parameters=["-q:a", "5"]
                )
            
            logger.info(f"音頻壓縮完成: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"音頻壓縮失敗: {str(e)}")
            return False

    @staticmethod
    async def compress_audio(input_path: str, output_path: str, aggressive: bool = False) -> bool:
        """異步壓縮音頻文件"""
        try:
            loop = asyncio.get_event_loop()
            with concurrent.futures.ThreadPoolExecutor() as executor:
                result = await loop.run_in_executor(
                    executor,
                    AudioProcessor._compress_audio_sync,
                    input_path,
                    output_path,
                    aggressive
                )
            return result
        except Exception as e:
            logger.error(f"異步壓縮音頻失敗: {str(e)}")
            return False