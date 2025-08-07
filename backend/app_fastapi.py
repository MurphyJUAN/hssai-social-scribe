# app_fastapi.py
from fastapi import FastAPI, UploadFile, File, HTTPException, Request
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import aiofiles
import tempfile
import os
import json
import time
import logging
from typing import List, AsyncGenerator, Dict, Any
import math
from pydub import AudioSegment
from pydub.effects import normalize
import io
from openai import AsyncOpenAI
import anthropic
from dotenv import load_dotenv
import concurrent.futures
from functools import partial

# 嘗試導入 backoff，如果沒有則定義一個簡單的重試裝飾器
try:
    import backoff
except ImportError:
    print("警告: 未安裝 backoff 庫，將使用簡單重試機制")
    
    def backoff_decorator(*args, **kwargs):
        def decorator(func):
            return func
        return decorator
    
    class backoff:
        expo = backoff_decorator
        on_exception = backoff_decorator

# 載入環境變數
load_dotenv()

# 設置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Social Work Report Generator",
    description="AI-powered social work report generation service",
    version="2.0.0"
)

# 添加 CORS 中間件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 檢查 API 金鑰
openai_api_key = os.getenv('OPENAI_API_KEY')
claude_api_key = os.getenv('CLAUDE_API_KEY')

if not openai_api_key:
    logger.error("❌ 未找到 OPENAI_API_KEY 環境變數")
    raise Exception("Missing OPENAI_API_KEY")

if not claude_api_key:
    logger.error("❌ 未找到 CLAUDE_API_KEY 環境變數")
    raise Exception("Missing CLAUDE_API_KEY")

# API 客戶端
openai_client = AsyncOpenAI(api_key=openai_api_key)
claude_client = anthropic.Anthropic(api_key=claude_api_key)

# 配置
MAX_CHUNK_SIZE = 15 * 1024 * 1024  # 15MB
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB 總限制
SUPPORTED_FORMATS = {'mp3', 'mp4', 'm4a', 'wav', 'webm', 'ogg', 'flac', 'aac'}
MAX_CONCURRENT_TRANSCRIPTIONS = 2  # 降低並發數
MAX_SEGMENT_MINUTES = 8  # 每段最大分鐘數

class IntegratedAudioProcessor:
    """完整整合的音頻處理器"""
    
    # ==================== 基礎音頻信息獲取 ====================
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
            # 嘗試使用 ffprobe 作為備選
            return IntegratedAudioProcessor._get_audio_info_with_ffprobe(file_path)
    
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
                    IntegratedAudioProcessor._get_audio_info_sync, 
                    file_path
                )
            return result
        except Exception as e:
            logger.error(f"獲取音頻信息失敗: {str(e)}")
            return {}

    # ==================== 音頻壓縮 ====================
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
                    IntegratedAudioProcessor._compress_audio_sync,
                    input_path,
                    output_path,
                    aggressive
                )
            return result
        except Exception as e:
            logger.error(f"異步壓縮音頻失敗: {str(e)}")
            return False

    # ==================== 智能分割 ====================
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
    async def smart_split_audio(file_path: str, duration_minutes: float, max_segment_minutes: int = MAX_SEGMENT_MINUTES) -> List[str]:
        """智能分割音頻 - 按時長分割"""
        try:
            logger.info(f"🎯 智能分割音頻: {file_path}, 總時長: {duration_minutes:.1f} 分鐘")
            
            # 如果不需要分割
            if not IntegratedAudioProcessor.should_split_by_duration(duration_minutes, os.path.getsize(file_path) / 1024 / 1024):
                logger.info("✅ 音頻時長適中，無需分割")
                return [file_path]
            
            # 計算分段數量
            num_segments = math.ceil(duration_minutes / max_segment_minutes)
            segment_duration_seconds = (duration_minutes * 60) / num_segments
            
            logger.info(f"📊 將分割為 {num_segments} 段，每段約 {segment_duration_seconds / 60:.1f} 分鐘")
            
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
    def _split_audio_by_size_sync(file_path: str, max_size: int) -> List[str]:
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
    async def split_audio_by_size(file_path: str, max_size: int) -> List[str]:
        """異步按文件大小分割音頻"""
        try:
            loop = asyncio.get_event_loop()
            with concurrent.futures.ThreadPoolExecutor() as executor:
                result = await loop.run_in_executor(
                    executor,
                    IntegratedAudioProcessor._split_audio_by_size_sync,
                    file_path,
                    max_size
                )
            return result
        except Exception as e:
            logger.error(f"異步分割音頻失敗: {str(e)}")
            return [file_path]

    # ==================== 轉換處理 ====================
    @staticmethod
    async def simple_retry_transcribe(chunk_path: str, chunk_index: int, max_retries: int = 3) -> tuple:
        """簡單重試機制的轉換"""
        last_error = None
        
        for attempt in range(max_retries):
            try:
                logger.info(f"🎯 轉換分段 {chunk_index} (第 {attempt + 1} 次嘗試): {chunk_path}")
                
                if not os.path.exists(chunk_path):
                    raise FileNotFoundError(f"分段文件不存在: {chunk_path}")
                
                file_size = os.path.getsize(chunk_path)
                logger.info(f"📏 分段 {chunk_index} 大小: {file_size / 1024 / 1024:.2f}MB")
                
                # 如果文件太大，嘗試額外壓縮
                processing_path = chunk_path
                if file_size > 8 * 1024 * 1024:  # 8MB
                    logger.warning(f"⚠️ 分段 {chunk_index} 過大，嘗試額外壓縮...")
                    extra_compressed_path = f"{chunk_path}_extra_compressed.mp3"
                    
                    success = await IntegratedAudioProcessor.compress_audio(chunk_path, extra_compressed_path, aggressive=True)
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
                    
                    response = await openai_client.audio.transcriptions.create(
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
                last_error = e
                error_str = str(e)
                logger.error(f"❌ 分段 {chunk_index} 轉換失敗 (嘗試 {attempt + 1}): {error_str}")
                
                # 根據錯誤類型決定是否重試
                if "502" in error_str or "Bad Gateway" in error_str:
                    if attempt < max_retries - 1:
                        wait_time = 2 ** attempt  # 指數退避
                        logger.info(f"🔄 502 錯誤，{wait_time} 秒後重試...")
                        await asyncio.sleep(wait_time)
                        continue
                elif "413" in error_str or "too large" in error_str.lower():
                    logger.error(f"💥 分段 {chunk_index} 檔案過大，跳過此分段")
                    return chunk_index, "[檔案過大，無法處理]", f"檔案過大: {error_str}"
                elif "timeout" in error_str.lower():
                    if attempt < max_retries - 1:
                        logger.info(f"⏰ 請求超時，重試...")
                        await asyncio.sleep(3)
                        continue
                
                # 其他錯誤，重試一次
                if attempt < max_retries - 1:
                    await asyncio.sleep(1)
                    continue
        
        # 所有重試都失敗
        error_msg = f"分段 {chunk_index} 所有重試都失敗: {str(last_error)}"
        logger.error(error_msg)
        return chunk_index, "", error_msg

def send_sse_data(data_type: str, **kwargs) -> str:
    """發送標準的 SSE 格式資料"""
    data = {
        'type': data_type,
        'timestamp': time.time(),
        **kwargs
    }
    
    try:
        # 確保 JSON 序列化正確
        json_str = json.dumps(data, ensure_ascii=False, separators=(',', ':'))
        
        # 標準 SSE 格式：data: + JSON + 雙換行符
        sse_message = f"data: {json_str}\n\n"
        
        # 記錄發送的數據 (僅在調試模式)
        if data_type in ['progress', 'complete', 'error']:
            logger.debug(f"📤 發送 SSE: {data_type} - {data.get('progress', 0)}% - {data.get('message', '')}")
        
        return sse_message
        
    except Exception as e:
        logger.error(f"❌ SSE 數據序列化失敗: {e}")
        # 返回錯誤消息
        error_data = {
            'type': 'error',
            'error': f'服務器內部錯誤: {str(e)}',
            'timestamp': time.time()
        }
        return f"data: {json.dumps(error_data)}\n\n"

async def process_large_audio_smart(file_path: str) -> AsyncGenerator[str, None]:
    """智能音頻處理 - 完整版本"""
    temp_files = []
    
    try:
        logger.info(f"🎬 開始智能處理音頻文件: {file_path}")
        
        # 1. 基本檢查
        file_size = os.path.getsize(file_path)
        yield send_sse_data('progress', progress=5, message=f'檔案大小: {file_size / 1024 / 1024:.1f}MB')
        
        # 2. 獲取音頻詳細信息
        audio_info = await IntegratedAudioProcessor.get_audio_info(file_path)
        duration_minutes = audio_info.get('duration_min', 0)
        
        if duration_minutes > 0:
            yield send_sse_data('progress', progress=10, 
                              message=f'音頻長度: {duration_minutes:.1f} 分鐘')
            
            if duration_minutes > 30:
                yield send_sse_data('progress', progress=12, 
                                  message='⚠️ 音頻較長，將採用智能分割策略')
            elif duration_minutes > 15:
                yield send_sse_data('progress', progress=12, 
                                  message='💡 音頻中等長度，將優化處理')
        
        # 3. 決定處理策略
        processing_file = file_path
        
        # 如果音頻很長，優先按時長分割
        if duration_minutes > 10:
            yield send_sse_data('progress', progress=15, message='採用時長分割策略...')
            
            chunks = await IntegratedAudioProcessor.smart_split_audio(file_path, duration_minutes, MAX_SEGMENT_MINUTES)
            temp_files.extend([chunk for chunk in chunks if chunk != file_path])
            
            yield send_sse_data('progress', progress=30, 
                              message=f'按時長分割完成，共 {len(chunks)} 段（每段約 {MAX_SEGMENT_MINUTES} 分鐘）')
        
        # 如果文件很大但時長不長，按大小分割
        elif file_size > MAX_CHUNK_SIZE:
            yield send_sse_data('progress', progress=15, message='檔案較大，先壓縮...')
            
            compressed_path = f"{file_path}_compressed.mp3"
            temp_files.append(compressed_path)
            
            success = await IntegratedAudioProcessor.compress_audio(file_path, compressed_path)
            if success and os.path.exists(compressed_path):
                processing_file = compressed_path
                new_size = os.path.getsize(compressed_path) / 1024 / 1024
                yield send_sse_data('progress', progress=25, 
                                  message=f'壓縮完成: {new_size:.1f}MB')
            
            # 檢查壓縮後是否還需要分割
            if os.path.getsize(processing_file) > MAX_CHUNK_SIZE:
                chunks = await IntegratedAudioProcessor.split_audio_by_size(processing_file, MAX_CHUNK_SIZE)
                temp_files.extend([chunk for chunk in chunks if chunk != file_path and chunk != processing_file])
            else:
                chunks = [processing_file]
            
            yield send_sse_data('progress', progress=30, 
                              message=f'處理準備完成，共 {len(chunks)} 段')
        
        else:
            # 小文件直接處理
            chunks = [file_path]
            yield send_sse_data('progress', progress=30, message='文件大小適中，直接處理')
        
        # 4. 驗證分段
        valid_chunks = []
        for i, chunk_path in enumerate(chunks):
            if os.path.exists(chunk_path) and os.path.getsize(chunk_path) > 1024:
                chunk_size = os.path.getsize(chunk_path) / 1024 / 1024
                valid_chunks.append((chunk_path, i))
                logger.info(f"✓ 有效分段 {i}: {chunk_size:.1f}MB")
            else:
                logger.error(f"✗ 無效分段 {i}: {chunk_path}")
        
        if not valid_chunks:
            raise ValueError("沒有有效的音頻分段")
        
        # 5. 智能轉換策略
        yield send_sse_data('progress', progress=35, 
                          message=f'開始轉換 {len(valid_chunks)} 個分段...')
        
        # 根據分段數量調整並發策略
        if len(valid_chunks) > 5:
            batch_size = 1  # 大量分段時串行處理
            delay_between_batches = 5
        elif len(valid_chunks) > 3:
            batch_size = 2
            delay_between_batches = 3
        else:
            batch_size = min(2, MAX_CONCURRENT_TRANSCRIPTIONS)
            delay_between_batches = 2
        
        logger.info(f"🎯 轉換策略: 批次大小={batch_size}, 延遲={delay_between_batches}秒")
        
        results = {}
        total_chunks = len(valid_chunks)
        processed_chunks = 0
        failed_chunks = 0
        
        for i in range(0, total_chunks, batch_size):
            batch_chunks = valid_chunks[i:i + batch_size]
            
            batch_info = f"第 {i//batch_size + 1}/{math.ceil(total_chunks/batch_size)} 批"
            yield send_sse_data('progress', 
                              progress=35 + (processed_chunks / total_chunks) * 50,
                              message=f'處理{batch_info} ({len(batch_chunks)} 段)...')
            
            # 執行轉換
            tasks = [
                IntegratedAudioProcessor.simple_retry_transcribe(chunk_path, chunk_idx, max_retries=3)
                for chunk_path, chunk_idx in batch_chunks
            ]
            
            try:
                max_timeout = max(120, max(os.path.getsize(cp) for cp, _ in batch_chunks) / 1024 / 1024 * 30)
                
                batch_results = await asyncio.wait_for(
                    asyncio.gather(*tasks, return_exceptions=True),
                    timeout=max_timeout
                )
            except asyncio.TimeoutError:
                logger.error(f"❌ 批次 {i//batch_size + 1} 超時")
                batch_results = [Exception("轉換超時") for _ in batch_chunks]
            
            # 處理結果
            for result in batch_results:
                if isinstance(result, Exception):
                    logger.error(f"❌ 批次處理異常: {result}")
                    failed_chunks += 1
                    continue
                    
                chunk_index, text, error = result
                if error:
                    logger.error(f"❌ 分段 {chunk_index} 錯誤: {error}")
                    failed_chunks += 1
                    if "檔案過大" not in error:
                        results[chunk_index] = ""  # 記錄失敗但繼續
                else:
                    results[chunk_index] = text
                    logger.info(f"✅ 分段 {chunk_index} 成功: {len(text)} 字")
                
                processed_chunks += 1
            
            # 更新進度
            progress = 35 + (processed_chunks / total_chunks) * 50
            success_rate = ((processed_chunks - failed_chunks) / processed_chunks * 100) if processed_chunks > 0 else 0
            yield send_sse_data('progress', progress=int(progress), 
                              message=f'已完成 {processed_chunks}/{total_chunks} 段 (成功率: {success_rate:.0f}%)')
            
            # 批次間延遲
            if i + batch_size < total_chunks:
                yield send_sse_data('progress', progress=int(progress), 
                                  message=f'暫停 {delay_between_batches} 秒，避免 API 限制...')
                await asyncio.sleep(delay_between_batches)
        
        # 6. 合併結果
        yield send_sse_data('progress', progress=90, message='合併轉換結果...')
        
        final_transcript = ""
        successful_chunks = processed_chunks - failed_chunks
        
        # 按順序合併
        for i in range(len(chunks)):
            if i in results and results[i]:
                final_transcript += results[i] + " "
        
        if successful_chunks == 0:
            raise Exception(f"所有 {total_chunks} 個分段都轉換失敗")
        
        final_transcript = final_transcript.strip()
        final_transcript = " ".join(final_transcript.split())
        
        success_rate = (successful_chunks / total_chunks) * 100
        
        # 7. 串流發送結果
        sentences = []
        for delimiter in ['。', '！', '？']:
            final_transcript = final_transcript.replace(delimiter, delimiter + '|')
        
        sentences = [s.strip() for s in final_transcript.split('|') if s.strip()]
        
        yield send_sse_data('progress', progress=95, 
                          message=f'開始發送結果... (共 {len(sentences)} 句)')
        
        for i, sentence in enumerate(sentences):
            if sentence:
                if not sentence.endswith(('。', '！', '？', '.', '!', '?')):
                    sentence += '。'
                
                yield send_sse_data('chunk', 
                                  text=sentence,
                                  progress=95 + (i / len(sentences)) * 5)
                await asyncio.sleep(0.03)
        
        # 8. 完成
        yield send_sse_data('complete', 
                          progress=100, 
                          message=f'處理完成！共 {len(final_transcript)} 字 (成功率: {success_rate:.1f}%)',
                          stats={
                              'original_duration_minutes': duration_minutes,
                              'total_chunks': total_chunks,
                              'successful_chunks': successful_chunks,
                              'failed_chunks': failed_chunks,
                              'success_rate': success_rate,
                              'total_characters': len(final_transcript),
                              'total_sentences': len(sentences),
                              'processing_strategy': 'time_based' if duration_minutes > 10 else 'size_based'
                          })
        
    except Exception as e:
        logger.error(f"智能音頻處理失敗: {str(e)}", exc_info=True)
        yield send_sse_data('error', 
                          error=f'處理失敗: {str(e)}',
                          error_type=type(e).__name__)
    
    finally:
        # 清理臨時文件
        for temp_file in temp_files:
            try:
                if temp_file and os.path.exists(temp_file):
                    os.unlink(temp_file)
                    logger.info(f"🗑️ 已刪除: {os.path.basename(temp_file)}")
            except Exception as e:
                logger.warning(f"清理失敗: {e}")

@app.post("/backend/transcribe")
async def transcribe_audio_smart(audio: UploadFile = File(...)):
    """智能音頻轉文字 API - 根據文件特性自動選擇最佳處理策略"""
    
    # 檢查文件名
    if not audio.filename:
        raise HTTPException(status_code=400, detail="沒有提供檔案名稱")
    
    # 檢查文件格式
    file_extension = audio.filename.split('.')[-1].lower()
    if file_extension not in SUPPORTED_FORMATS:
        raise HTTPException(
            status_code=400, 
            detail=f"不支援的檔案格式。支援格式: {', '.join(SUPPORTED_FORMATS)}"
        )
    
    # 讀取文件內容並檢查大小
    content = await audio.read()
    file_size = len(content)
    
    logger.info(f"📁 收到音頻文件: {audio.filename}, 大小: {file_size / 1024 / 1024:.2f}MB")
    
    # 檢查文件大小限制
    if file_size > MAX_FILE_SIZE:
        logger.warning(f"❌ 文件過大: {file_size / 1024 / 1024:.2f}MB > {MAX_FILE_SIZE / 1024 / 1024}MB")
        raise HTTPException(
            status_code=413,
            detail=f"檔案大小超過限制 ({MAX_FILE_SIZE // (1024*1024)}MB)"
        )
    
    if file_size == 0:
        logger.error("❌ 文件為空")
        raise HTTPException(status_code=400, detail="上傳的文件為空")
    
    # 保存上傳的文件到臨時位置
    with tempfile.NamedTemporaryFile(delete=False, suffix=f".{file_extension}") as tmp_file:
        tmp_file.write(content)
        temp_file_path = tmp_file.name
    
    logger.info(f"💾 文件已保存到: {temp_file_path}")
    
    async def generate_response():
        try:
            yield send_sse_data('progress', progress=0, message='正在分析音頻文件...')
            
            # 使用智能處理函數
            async for chunk in process_large_audio_smart(temp_file_path):
                yield chunk
                
        except Exception as e:
            logger.error(f"處理錯誤: {str(e)}", exc_info=True)
            
            # 提供更詳細的錯誤信息
            error_message = str(e)
            if "502" in error_message or "Bad Gateway" in error_message:
                error_message = "OpenAI 服務暫時不可用，請稍後再試"
            elif "timeout" in error_message.lower():
                error_message = "請求超時，檔案可能過大，建議分段上傳"
            elif "413" in error_message or "too large" in error_message.lower():
                error_message = "檔案過大，請壓縮後再試或分段上傳"
            
            yield send_sse_data('error', error=error_message)
            
        finally:
            try:
                if os.path.exists(temp_file_path):
                    os.unlink(temp_file_path)
                    logger.info(f"🗑️ 已清理原始文件: {temp_file_path}")
            except Exception as e:
                logger.warning(f"⚠️ 清理上傳文件失敗: {e}")
    
    return StreamingResponse(
        generate_response(),
        media_type='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Content-Type': 'text/event-stream; charset=utf-8',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Cache-Control',
            'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
            'X-Accel-Buffering': 'no'
        }
    )

def load_prompt_templates(filename):
    """載入 prompt 模板"""
    try:
        with open(f'prompts/{filename}', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        logger.error(f"找不到 prompts/{filename} 檔案")
        return None
    except json.JSONDecodeError:
        logger.error(f"prompts/{filename}' 格式錯誤")
        return None
    
def build_report_prompt(transcript, social_worker_notes, selected_sections, required_sections):
    """建構記錄生成的 prompt"""
    templates = load_prompt_templates(filename="report_prompts.json")
    if not templates:
        raise Exception("無法載入 prompt 模板")
    
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
        input_content += f"\n\n社工補充說明：\n{social_worker_notes}"
    
    # 替換 input 變數
    full_prompt = full_prompt.replace('{input}', input_content)
    
    return full_prompt


# 保持其他 API 端點 (記錄生成、處遇計畫等)
async def generate_report_streaming(transcript: str, social_worker_notes: str, 
                                  selected_sections: List[str], required_sections: List[str]):
    """生成記錄 (保持原有邏輯)"""
    try:
        yield send_sse_data('progress', progress=10, message='準備生成記錄...')
        
        # 簡化的 prompt (你可以根據需要修改)
        prompt = build_report_prompt(transcript, social_worker_notes, selected_sections, required_sections)
        
        yield send_sse_data('progress', progress=20, message='正在生成記錄...')
        
        # 調用 Claude API
        with claude_client.messages.stream(
            model="claude-3-sonnet-20240229",
            max_tokens=4000,
            temperature=0.3,
            messages=[{"role": "user", "content": prompt}]
        ) as stream:
            
            current_progress = 30
            for event in stream:
                if event.type == "content_block_delta":
                    text_chunk = event.delta.text
                    yield send_sse_data('chunk', text=text_chunk, progress=min(95, current_progress))
                    current_progress += 0.5
                elif event.type == "message_stop":
                    yield send_sse_data('complete', progress=100, message='記錄生成完成')
                    break
                    
    except Exception as e:
        logger.error(f"記錄生成失敗: {str(e)}")
        yield send_sse_data('error', error=f'記錄生成失敗: {str(e)}')

@app.post("/backend/generate-report")
async def generate_report(request: Request):
    """生成記錄初稿 API"""
    try:
        data = await request.json()
        
        transcript = data.get('transcript', '').strip()
        if not transcript:
            raise HTTPException(status_code=400, detail="逐字稿內容不能為空")
        
        social_worker_notes = data.get('socialWorkerNotes', '').strip()
        selected_sections = data.get('selectedSections', [])
        required_sections = data.get('requiredSections', [])
        
        async def generate_response():
            async for chunk in generate_report_streaming(transcript, social_worker_notes, selected_sections, required_sections):
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

@app.get("/backend/health")
async def health_check():
    """健康檢查"""
    return {
        'status': 'healthy',
        'service': 'social-work-report-generator-fastapi',
        'timestamp': time.time(),
        'version': '2.0.0',
        'apis': ['transcribe', 'generate-report', 'generate-treatment-plan'],
        'features': ['large_file_support', 'audio_compression', 'concurrent_processing']
    }

@app.get("/backend/supported-formats")
async def get_supported_formats():
    """獲取支援的格式和配置"""
    return {
        'supported_formats': list(SUPPORTED_FORMATS),
        'max_file_size_mb': MAX_FILE_SIZE // (1024*1024),
        'max_chunk_size_mb': MAX_CHUNK_SIZE // (1024*1024),
        'max_concurrent_transcriptions': MAX_CONCURRENT_TRANSCRIPTIONS
    }

if __name__ == "__main__":
    import uvicorn
    
    logger.info("🚀 啟動 FastAPI 社工報告生成服務...")
    logger.info(f"✅ OpenAI API 金鑰已載入")
    logger.info(f"✅ Claude API 金鑰已載入")
    
    # 修正的啟動方式
    uvicorn.run(
        "app_fastapi:app",  # 使用字符串形式
        host="0.0.0.0", 
        port=5174,
        reload=True,        # 現在可以正常使用 reload
        log_level="info",
        access_log=True     # 顯示訪問日誌
    )