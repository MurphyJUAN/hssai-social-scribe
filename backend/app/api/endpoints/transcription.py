# ================================
# 11. app/api/endpoints/transcription.py - 轉錄端點
# ================================

import os
import math
import asyncio
import logging
from typing import List
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.responses import StreamingResponse

from app.config import Config
from app.dependencies import get_openai_client
from core.utils.sse import send_sse_data
from core.utils.file_utils import save_upload_file, cleanup_files, validate_audio_file
from core.audio.processor import AudioProcessor
from core.audio.splitter import AudioSplitter
from core.audio.transcriber import AudioTranscriber
from core.utils.text_converter import text_converter

logger = logging.getLogger(__name__)

router = APIRouter()

class TranscriptionService:
    """轉錄服務主邏輯"""
    
    def __init__(self, openai_client):
        self.transcriber = AudioTranscriber(openai_client)
    
    async def process_audio_smart(self, file_path: str):
        """智能音頻處理 - 主要邏輯"""
        temp_files = []
        
        try:
            logger.info(f"🎬 開始智能處理音頻文件: {file_path}")
            
            # 1. 基本檢查
            file_size = os.path.getsize(file_path)
            yield send_sse_data('progress', progress=5, message=f'檔案大小: {file_size / 1024 / 1024:.1f}MB')
            
            # 2. 獲取音頻詳細信息
            audio_info = await AudioProcessor.get_audio_info(file_path)
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
                
                chunks = await AudioSplitter.smart_split_by_duration(
                    file_path, duration_minutes, Config.MAX_SEGMENT_MINUTES
                )
                temp_files.extend([chunk for chunk in chunks if chunk != file_path])
                
                yield send_sse_data('progress', progress=30, 
                                  message=f'按時長分割完成，共 {len(chunks)} 段（每段約 {Config.MAX_SEGMENT_MINUTES} 分鐘）')
            
            # 如果文件很大但時長不長，按大小分割
            elif file_size > Config.MAX_CHUNK_SIZE:
                yield send_sse_data('progress', progress=15, message='檔案較大，先壓縮...')
                
                compressed_path = f"{file_path}_compressed.mp3"
                temp_files.append(compressed_path)
                
                success = await AudioProcessor.compress_audio(file_path, compressed_path)
                if success and os.path.exists(compressed_path):
                    processing_file = compressed_path
                    new_size = os.path.getsize(compressed_path) / 1024 / 1024
                    yield send_sse_data('progress', progress=25, 
                                      message=f'壓縮完成: {new_size:.1f}MB')
                
                # 檢查壓縮後是否還需要分割
                if os.path.getsize(processing_file) > Config.MAX_CHUNK_SIZE:
                    chunks = await AudioSplitter.split_by_size(processing_file, Config.MAX_CHUNK_SIZE)
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
            batch_size, delay_between_batches = self._get_batch_strategy(len(valid_chunks))
            
            logger.info(f"🎯 轉換策略: 批次大小={batch_size}, 延遲={delay_between_batches}秒")
            
            results = {}
            total_chunks = len(valid_chunks)
            processed_chunks = 0
            failed_chunks = 0
            
            # 6. 批次處理轉錄
            for i in range(0, total_chunks, batch_size):
                batch_chunks = valid_chunks[i:i + batch_size]
                
                batch_info = f"第 {i//batch_size + 1}/{math.ceil(total_chunks/batch_size)} 批"
                yield send_sse_data('progress', 
                                  progress=35 + (processed_chunks / total_chunks) * 50,
                                  message=f'處理{batch_info} ({len(batch_chunks)} 段)...')
                
                # 執行轉換
                tasks = [
                    self.transcriber.transcribe_chunk_with_retry(chunk_path, chunk_idx, max_retries=3)
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
            
            # 7. 合併和輸出結果
            async for chunk in self._finalize_results(results, chunks, total_chunks, failed_chunks, duration_minutes):
                yield chunk
                
        except Exception as e:
            logger.error(f"智能音頻處理失敗: {str(e)}", exc_info=True)
            yield send_sse_data('error', 
                              error=f'處理失敗: {str(e)}',
                              error_type=type(e).__name__)
        
        finally:
            # 清理臨時文件
            cleanup_files(temp_files)
    
    def _get_batch_strategy(self, chunk_count: int):
        """根據分段數量獲取批次策略"""
        if chunk_count > 5:
            return 1, 5  # 大量分段時串行處理
        elif chunk_count > 3:
            return 2, 3
        else:
            return min(2, Config.MAX_CONCURRENT_TRANSCRIPTIONS), 2
    
    async def _finalize_results(self, results, chunks, total_chunks, failed_chunks, duration_minutes):
        """最終化結果"""
        yield send_sse_data('progress', progress=90, message='合併轉換結果...')
        
        final_transcript = ""
        successful_chunks = len([r for r in results.values() if r])
        
        # 按順序合併
        for i in range(len(chunks)):
            if i in results and results[i]:
                final_transcript += results[i] + " "
        
        if successful_chunks == 0:
            raise Exception(f"所有 {total_chunks} 個分段都轉換失敗")
        
        final_transcript = final_transcript.strip()
        final_transcript = " ".join(final_transcript.split())

        yield send_sse_data('progress', progress=92, message='轉換為繁體中文...')
        final_transcript = text_converter.to_traditional(final_transcript)
        logger.info(f"✅ 已轉換為繁體中文，共 {len(final_transcript)} 字")
        
        success_rate = (successful_chunks / total_chunks) * 100
        
        # 串流發送結果
        sentences = self._split_into_sentences(final_transcript)
        
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
        
        # 完成
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
    
    def _split_into_sentences(self, text: str) -> List[str]:
        """將文本分割成句子"""
        sentences = []
        for delimiter in ['。', '！', '？']:
            text = text.replace(delimiter, delimiter + '|')
        
        sentences = [s.strip() for s in text.split('|') if s.strip()]
        return sentences


@router.post("/transcribe")
async def transcribe_audio_smart(
    audio: UploadFile = File(...),
    openai_client = Depends(get_openai_client)
):
    """智能音頻轉文字 API - 修復版本"""
    
    # 🔑 修復：先讀取內容進行驗證，然後重置指針
    content = await audio.read()
    file_size = len(content)
    
    try:
        validate_audio_file(audio.filename, file_size, Config.SUPPORTED_FORMATS, Config.MAX_FILE_SIZE)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    logger.info(f"📁 收到音頻文件: {audio.filename}, 大小: {file_size / 1024 / 1024:.2f}MB")
    
    # 🔑 修復：重置文件指針，然後保存文件
    await audio.seek(0)  # 重要：重置文件指針到開頭
    file_extension = audio.filename.split('.')[-1].lower()
    temp_file_path = await save_upload_file(audio, suffix=f".{file_extension}")
    
    # 創建轉錄服務
    service = TranscriptionService(openai_client)
    
    async def generate_response():
        try:
            yield send_sse_data('progress', progress=0, message='正在分析音頻文件...')
            
            # 使用智能處理函數
            async for chunk in service.process_audio_smart(temp_file_path):
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
            cleanup_files([temp_file_path])
    
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
