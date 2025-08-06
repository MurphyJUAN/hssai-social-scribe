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
MAX_CONCURRENT_TRANSCRIPTIONS = 3  # OpenAI API 並發限制

class AudioProcessor:
    """修復的音頻處理類"""
    
    @staticmethod
    def _get_audio_info_sync(file_path: str) -> Dict[str, Any]:
        """同步獲取音頻文件信息"""
        try:
            from pydub import AudioSegment
            audio = AudioSegment.from_file(file_path)
            
            return {
                'duration_ms': len(audio),
                'duration_min': len(audio) / 1000 / 60,
                'channels': audio.channels,
                'frame_rate': audio.frame_rate,
                'sample_width': audio.sample_width
            }
        except Exception as e:
            logger.error(f"同步獲取音頻信息失敗: {str(e)}")
            return {}
    
    @staticmethod
    async def get_audio_info(file_path: str) -> Dict[str, Any]:
        """異步獲取音頻文件信息"""
        try:
            # 在線程池中運行同步函數
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
    def _compress_audio_sync(input_path: str, output_path: str) -> bool:
        """同步壓縮音頻文件"""
        try:
            from pydub import AudioSegment
            from pydub.effects import normalize
            
            logger.info(f"開始壓縮音頻: {input_path}")
            
            # 載入音頻
            audio = AudioSegment.from_file(input_path)
            logger.info(f"原始音頻: {len(audio)}ms, {audio.channels}聲道, {audio.frame_rate}Hz")
            
            # 壓縮設置：針對語音識別優化
            # 1. 降低採樣率到 16kHz (語音識別最佳)
            if audio.frame_rate > 16000:
                audio = audio.set_frame_rate(16000)
            
            # 2. 轉換為單聲道
            if audio.channels > 1:
                audio = audio.set_channels(1)
            
            # 3. 正規化音量
            audio = normalize(audio)
            
            # 導出為壓縮格式
            audio.export(
                output_path,
                format="mp3",
                bitrate="64k",
                parameters=["-q:a", "5"]  # 中等壓縮率，保持品質
            )
            
            logger.info(f"音頻壓縮完成: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"同步壓縮音頻失敗: {str(e)}")
            return False

    @staticmethod
    async def compress_audio(input_path: str, output_path: str) -> bool:
        """異步壓縮音頻文件"""
        try:
            loop = asyncio.get_event_loop()
            with concurrent.futures.ThreadPoolExecutor() as executor:
                result = await loop.run_in_executor(
                    executor,
                    AudioProcessor._compress_audio_sync,
                    input_path,
                    output_path
                )
            return result
        except Exception as e:
            logger.error(f"異步壓縮音頻失敗: {str(e)}")
            return False

    @staticmethod
    def _split_audio_sync(file_path: str, max_size: int) -> List[str]:
        """同步分割音頻"""
        try:
            from pydub import AudioSegment
            
            logger.info(f"開始分割音頻: {file_path}, 最大大小: {max_size / 1024 / 1024:.1f}MB")
            
            # 載入音頻
            audio = AudioSegment.from_file(file_path)
            
            # 計算需要分割的段數
            file_size = os.path.getsize(file_path)
            logger.info(f"檔案大小: {file_size / 1024 / 1024:.1f}MB")
            
            if file_size <= max_size:
                logger.info("檔案小於限制，無需分割")
                return [file_path]
            
            num_chunks = math.ceil(file_size / max_size)
            logger.info(f"需要分割為 {num_chunks} 段")
            
            # 計算每段的時長 (毫秒)
            duration_per_chunk = len(audio) // num_chunks
            
            chunks = []
            for i in range(num_chunks):
                start_time = i * duration_per_chunk
                end_time = start_time + duration_per_chunk if i < num_chunks - 1 else len(audio)
                
                logger.info(f"創建分段 {i}: {start_time}ms - {end_time}ms")
                
                # 提取音頻段
                chunk = audio[start_time:end_time]
                
                # 保存分段
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
            logger.error(f"同步分割音頻失敗: {str(e)}", exc_info=True)
            return [file_path]  # 返回原文件

    @staticmethod
    async def split_audio_by_size(file_path: str, max_size: int) -> List[str]:
        """異步按文件大小分割音頻"""
        try:
            loop = asyncio.get_event_loop()
            with concurrent.futures.ThreadPoolExecutor() as executor:
                result = await loop.run_in_executor(
                    executor,
                    AudioProcessor._split_audio_sync,
                    file_path,
                    max_size
                )
            return result
        except Exception as e:
            logger.error(f"異步分割音頻失敗: {str(e)}")
            return [file_path]

    @staticmethod
    async def transcribe_chunk(chunk_path: str, chunk_index: int) -> tuple:
        """轉換單個音頻分段"""
        try:
            logger.info(f"開始轉換分段 {chunk_index}: {chunk_path}")
            
            # 檢查文件是否存在
            if not os.path.exists(chunk_path):
                raise FileNotFoundError(f"分段文件不存在: {chunk_path}")
            
            # 檢查文件大小
            file_size = os.path.getsize(chunk_path)
            logger.info(f"分段 {chunk_index} 大小: {file_size / 1024 / 1024:.2f}MB")
            
            # 讀取文件
            async with aiofiles.open(chunk_path, 'rb') as audio_file:
                audio_data = await audio_file.read()
                
                if not audio_data:
                    raise ValueError(f"分段文件為空: {chunk_path}")
                
                # 創建 BytesIO 對象
                audio_io = io.BytesIO(audio_data)
                audio_io.name = f"chunk_{chunk_index}.mp3"
                
                logger.info(f"發送分段 {chunk_index} 到 OpenAI...")
                
                # 調用 OpenAI API
                response = await openai_client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_io,
                    response_format="verbose_json",
                    language="zh"
                )
                
                text = response.text
                logger.info(f"分段 {chunk_index} 轉換完成，文字長度: {len(text)}")
                
                return chunk_index, text, None
                
        except Exception as e:
            error_msg = f"分段 {chunk_index} 轉換失敗: {str(e)}"
            logger.error(error_msg, exc_info=True)
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

async def process_large_audio(file_path: str) -> AsyncGenerator[str, None]:
    """處理大型音頻文件的主要函數 (修復版)"""
    temp_files = []
    
    try:
        logger.info(f"開始處理音頻文件: {file_path}")
        
        # 1. 檢查文件是否存在
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"音頻文件不存在: {file_path}")
        
        # 2. 檢查文件大小
        file_size = os.path.getsize(file_path)
        if file_size == 0:
            raise ValueError("音頻文件為空")
        
        yield send_sse_data('progress', 
                          progress=5, 
                          message=f'檔案大小: {file_size / 1024 / 1024:.1f}MB')
        
        # 3. 獲取音頻信息 (可選，失敗不影響主流程)
        try:
            audio_info = await AudioProcessor.get_audio_info(file_path)
            if audio_info:
                duration_min = audio_info.get('duration_min', 0)
                yield send_sse_data('progress', 
                                  progress=8, 
                                  message=f'音頻長度: {duration_min:.1f} 分鐘')
        except Exception as e:
            logger.warning(f"獲取音頻信息失敗，繼續處理: {e}")
        
        # 4. 如果文件較大，先壓縮
        processing_file = file_path
        if file_size > MAX_CHUNK_SIZE:
            yield send_sse_data('progress', progress=10, message='檔案較大，開始壓縮...')
            
            compressed_path = f"{file_path}_compressed.mp3"
            temp_files.append(compressed_path)
            
            success = await AudioProcessor.compress_audio(file_path, compressed_path)
            if success and os.path.exists(compressed_path):
                new_size = os.path.getsize(compressed_path)
                if new_size > 0:  # 確保壓縮後的文件不為空
                    processing_file = compressed_path
                    compression_ratio = (1 - new_size / file_size) * 100
                    yield send_sse_data('progress', progress=20, 
                                      message=f'壓縮完成，大小: {new_size / 1024 / 1024:.1f}MB (壓縮 {compression_ratio:.1f}%)')
                else:
                    logger.warning("壓縮後文件為空，使用原文件")
                    yield send_sse_data('progress', progress=20, message='壓縮後文件異常，使用原文件')
            else:
                logger.warning("壓縮失敗，使用原文件")
                yield send_sse_data('progress', progress=20, message='壓縮失敗，使用原文件')
        
        # 5. 分割音頻
        yield send_sse_data('progress', progress=25, message='準備分割音頻...')
        chunks = await AudioProcessor.split_audio_by_size(processing_file, MAX_CHUNK_SIZE)
        
        # 清理分段文件列表，排除原文件
        chunk_temp_files = [chunk for chunk in chunks if chunk != file_path and chunk != processing_file]
        temp_files.extend(chunk_temp_files)
        
        if len(chunks) > 1:
            yield send_sse_data('progress', progress=30, 
                              message=f'音頻已分割為 {len(chunks)} 段')
        else:
            yield send_sse_data('progress', progress=30, message='音頻無需分割')
        
        # 6. 驗證所有分段文件
        valid_chunks = []
        for i, chunk_path in enumerate(chunks):
            if os.path.exists(chunk_path) and os.path.getsize(chunk_path) > 0:
                valid_chunks.append((chunk_path, i))
            else:
                logger.error(f"分段文件無效: {chunk_path}")
        
        if not valid_chunks:
            raise ValueError("沒有有效的音頻分段")
        
        # 7. 並發轉換所有有效分段
        yield send_sse_data('progress', progress=35, message='開始轉換音頻為文字...')
        
        batch_size = MAX_CONCURRENT_TRANSCRIPTIONS
        results = {}
        total_chunks = len(valid_chunks)
        processed_chunks = 0
        
        for i in range(0, total_chunks, batch_size):
            batch_chunks = valid_chunks[i:i + batch_size]
            
            # 創建當前批次的任務
            tasks = [
                AudioProcessor.transcribe_chunk(chunk_path, chunk_idx) 
                for chunk_path, chunk_idx in batch_chunks
            ]
            
            yield send_sse_data('progress', 
                              progress=35 + (processed_chunks / total_chunks) * 50,
                              message=f'處理第 {i//batch_size + 1} 批，共 {len(batch_chunks)} 段')
            
            # 並發執行當前批次
            batch_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # 處理批次結果
            for result in batch_results:
                if isinstance(result, Exception):
                    logger.error(f"批次處理異常: {result}")
                    continue
                    
                chunk_index, text, error = result
                if error:
                    logger.error(f"分段處理錯誤: {error}")
                    results[chunk_index] = f"[分段 {chunk_index} 處理失敗]"
                else:
                    results[chunk_index] = text
                
                processed_chunks += 1
                progress = 35 + (processed_chunks / total_chunks) * 50
                yield send_sse_data('progress', progress=int(progress), 
                                  message=f'已完成 {processed_chunks}/{total_chunks} 段')
            
            # 批次間延遲
            if i + batch_size < total_chunks:
                await asyncio.sleep(1)
        
        # 8. 合併結果
        yield send_sse_data('progress', progress=90, message='合併轉換結果...')
        
        final_transcript = ""
        successful_chunks = 0
        
        # 按順序合併結果
        for i in range(len(chunks)):
            if i in results and results[i] and not results[i].startswith("[分段"):
                final_transcript += results[i] + " "
                successful_chunks += 1
        
        if successful_chunks == 0:
            raise Exception("所有音頻分段轉換都失敗了")
        
        # 9. 清理並格式化文字
        final_transcript = final_transcript.strip()
        final_transcript = " ".join(final_transcript.split())
        
        yield send_sse_data('progress', progress=95, 
                          message=f'轉換完成，成功處理 {successful_chunks}/{len(chunks)} 段')
        
        # 10. 模擬串流發送文字
        sentences = []
        for delimiter in ['。', '！', '？']:
            final_transcript = final_transcript.replace(delimiter, delimiter + '|')
        
        sentences = [s.strip() for s in final_transcript.split('|') if s.strip()]
        
        for i, sentence in enumerate(sentences):
            if sentence:
                if not sentence.endswith(('。', '！', '？', '.', '!', '?')):
                    sentence += '。'
                
                yield send_sse_data('chunk', 
                                  text=sentence,
                                  progress=95 + (i / len(sentences)) * 5)
                await asyncio.sleep(0.05)
        
        # 11. 完成
        yield send_sse_data('complete', 
                          progress=100, 
                          message=f'轉換完成，共 {len(final_transcript)} 字',
                          stats={
                              'total_chunks': len(chunks),
                              'successful_chunks': successful_chunks,
                              'total_characters': len(final_transcript),
                              'total_sentences': len(sentences)
                          })
        
    except Exception as e:
        logger.error(f"音頻處理失敗: {str(e)}", exc_info=True)
        yield send_sse_data('error', 
                          error=f'音頻處理失敗: {str(e)}',
                          error_type=type(e).__name__)
    
    finally:
        # 清理所有臨時文件
        if temp_files:
            yield send_sse_data('progress', progress=100, message='清理臨時文件...')
            
            for temp_file in temp_files:
                try:
                    if temp_file and os.path.exists(temp_file):
                        os.unlink(temp_file)
                        logger.info(f"已刪除臨時文件: {temp_file}")
                except Exception as e:
                    logger.warning(f"清理臨時文件失敗 {temp_file}: {e}")

@app.post("/api/transcribe")
async def transcribe_audio(audio: UploadFile = File(...)):
    """音頻轉文字 API (支持大文件分段處理) - 修復版"""
    
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
    
    # 記錄文件信息 (在 file_size 定義之後)
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
            # 發送初始狀態
            yield send_sse_data('progress', 
                              progress=0, 
                              message=f'開始處理音頻文件 ({file_size / 1024 / 1024:.1f}MB)...')
            
            # 處理音頻文件
            async for chunk in process_large_audio(temp_file_path):
                yield chunk
                
        except Exception as e:
            logger.error(f"❌ 處理過程發生錯誤: {str(e)}", exc_info=True)
            yield send_sse_data('error', error=f'處理失敗: {str(e)}')
            
        finally:
            # 清理原始上傳文件
            try:
                if os.path.exists(temp_file_path):
                    os.unlink(temp_file_path)
                    logger.info(f"🗑️ 已清理臨時文件: {temp_file_path}")
            except Exception as e:
                logger.warning(f"⚠️ 清理上傳文件失敗: {e}")
    
    # 返回 SSE 響應
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
            'X-Accel-Buffering': 'no'  # 禁用反向代理緩衝
        }
    )


# 保持其他 API 端點 (記錄生成、處遇計畫等)
async def generate_report_streaming(transcript: str, social_worker_notes: str, 
                                  selected_sections: List[str], required_sections: List[str]):
    """生成記錄 (保持原有邏輯)"""
    try:
        yield send_sse_data('progress', progress=10, message='準備生成記錄...')
        
        # 簡化的 prompt (你可以根據需要修改)
        prompt = f"""
        請根據以下訪談逐字稿生成專業的社工記錄：
        
        逐字稿：
        {transcript}
        
        {'社工補充說明：' + social_worker_notes if social_worker_notes else ''}
        
        請生成結構化的社工記錄，包括個案基本情況、問題分析、需求評估等。
        """
        
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

@app.post("/api/generate-report")
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

@app.get("/api/health")
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

@app.get("/api/supported-formats")
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