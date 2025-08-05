# app.py
from flask import Flask, request, Response, jsonify
from flask_cors import CORS
import os
import json
import time
import tempfile
import logging
from werkzeug.utils import secure_filename
from openai import OpenAI
import mimetypes
from dotenv import load_dotenv
import anthropic

# 載入 .env 檔案中的環境變數
load_dotenv()

# 設置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # 允許跨域請求

# 檢查並設置 OpenAI API 金鑰
openai_api_key = os.getenv('OPENAI_API_KEY')
if not openai_api_key:
    logger.error("❌ 錯誤: 未找到 OPENAI_API_KEY 環境變數")
    logger.error("請確保 .env 檔案存在且包含 OPENAI_API_KEY=your_api_key")
    exit(1)

# 檢查並設置 Claude API 金鑰
claude_api_key = os.getenv('CLAUDE_API_KEY')
if not claude_api_key:
    logger.error("❌ 錯誤: 未找到 CLAUDE_API_KEY 環境變數")
    logger.error("請確保 .env 檔案存在且包含 CLAUDE_API_KEY=your_api_key")
    exit(1)

logger.info(f"✅ OpenAI API 金鑰已載入: {openai_api_key[:8]}...")
logger.info(f"✅ Claude API 金鑰已載入: {claude_api_key[:8]}...")

# 設置 API 客戶端
openai_client = OpenAI(api_key=openai_api_key)
claude_client = anthropic.Anthropic(api_key=claude_api_key)

# 支援的音檔格式
ALLOWED_EXTENSIONS = {
    'mp3', 'mp4', 'm4a', 'wav', 'webm', 'ogg', 'flac', 'aac'
}

# 檔案大小限制 (100MB)
MAX_FILE_SIZE = 100 * 1024 * 1024

def allowed_file(filename):
    """檢查檔案格式是否支援"""
    if '.' not in filename:
        return False
    extension = filename.rsplit('.', 1)[1].lower()
    return extension in ALLOWED_EXTENSIONS

def get_file_size(file):
    """獲取檔案大小"""
    file.seek(0, 2)  # 移到檔案末尾
    size = file.tell()
    file.seek(0)  # 回到檔案開頭
    return size

def send_sse_data(data_type, **kwargs):
    """發送 SSE 格式的資料"""
    data = {
        'type': data_type,
        **kwargs
    }
    return f"data: {json.dumps(data, ensure_ascii=False)}\n\n"

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

def build_treatment_prompt(transcript, report_draft, selected_service_domains, social_worker_notes):
    """建構處遇計畫生成的 prompt"""
    
    # 服務領域對照表
    service_domains_mapping = {
        'judicial_correction': '司法與矯治',
        'economic_assistance': '經濟扶助',
        'immigrant_indigenous': '新(原)住民',
        'protection_services': '保護服務',
        'children_youth': '兒童與少年',
        'school_education': '學校與教育',
        'women_family': '婦女與家庭',
        'medical_related': '醫務相關',
        'psychological_mental': '心理與精神',
        'disability': '身心障礙',
        'elderly_longterm_care': '老人與長照'
    }
    
    # 將選擇的服務領域轉換為中文
    selected_domains_text = ', '.join([
        service_domains_mapping.get(domain, domain) 
        for domain in selected_service_domains
    ])
    
    # 基本 prompt 模板
    base_prompt = """根據以下社工報告，請生成專業的處遇計畫。

撰寫風格要求：
1. 使用純文字格式，不要使用任何 Markdown 符號或特殊標記
2. 以陳述性段落撰寫，避免過度使用條列式格式
3. 採用客觀、清晰的第三人稱文風
4. 對於推測或判斷，請明確使用「可能」、「預期」、「似乎」、「推測」等字樣表達
5. 每個段落應該連貫且具有邏輯性

處遇計畫應該包含以下結構：

一、處遇目標
以段落形式陳述短期目標（1-3個月）、中期目標（3-6個月）、長期目標（6個月以上）。每個目標應該具體、可測量、可達成，並說明目標設定的理由和預期達成方式。

二、處遇策略
以連貫的段落描述個案工作策略、家族治療策略、資源連結策略、環境調整策略等。每項策略應說明實施方法、理論依據以及與個案狀況的適配性。

三、實施步驟
按時間順序以段落形式說明評估階段、介入階段、維持階段、結案評估等各階段的工作重點、預期時程以及具體執行方式。

四、預期成效
以段落形式陳述個人層面成效、家庭層面成效、社會功能改善、風險降低程度等預期結果。對於每項成效都應說明評估依據和達成指標。

五、評估指標
以段落形式說明量化指標和質化指標的設定，包括時程安排和檢核方式。指標應該客觀、可操作，並能有效反映處遇成效。

六、資源需求
以段落形式說明人力資源、經費需求、外部資源、專業協助等各項資源配置，包括資源取得方式和使用規劃。

撰寫要求：
請根據報告中的具體問題和需求制定切實可行的處遇計畫。目標設定應該具體、可測量、可達成。策略應該具有專業性和可操作性。時程安排要合理且具有彈性。充分考慮案主的能力、資源和限制。體現社會工作的專業價值和倫理。內容應以連貫的段落形式呈現，避免使用任何格式化符號。

特別考量的服務領域：{selected_domains}

請基於以下內容生成處遇計畫：

{input}"""
    
    # 建構輸入內容
    input_content = ""
    
    if report_draft and report_draft.strip():
        input_content += f"社工記錄報告：\n{report_draft}\n\n"
    
    if transcript and transcript.strip():
        input_content += f"原始逐字稿：\n{transcript}\n\n"
    
    if social_worker_notes and social_worker_notes.strip():
        input_content += f"社工補充說明：\n{social_worker_notes}"
    
    # 替換變數
    full_prompt = base_prompt.replace('{selected_domains}', selected_domains_text)
    full_prompt = full_prompt.replace('{input}', input_content)
    
    return full_prompt

def generate_report_streaming(transcript, social_worker_notes, selected_sections, required_sections):
    """使用 Claude API 生成記錄並串流回傳"""
    try:
        # 發送開始生成的訊息
        yield send_sse_data('progress', progress=10, message='準備生成記錄...')
        
        # 建構 prompt
        prompt = build_report_prompt(transcript, social_worker_notes, selected_sections, required_sections)
        
        yield send_sse_data('progress', progress=20, message='正在請求 AI 生成記錄...')
        
        # 調用 Claude API
        with claude_client.messages.stream(
            model="claude-4-sonnet-20250514",
            max_tokens=4000,
            temperature=0.3,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        ) as stream:
            
            current_progress = 30
            accumulated_text = ""
            
            for event in stream:
                if event.type == "content_block_delta":
                    text_chunk = event.delta.text
                    accumulated_text += text_chunk
                    
                    # 發送文字片段
                    yield send_sse_data(
                        'chunk',
                        text=text_chunk,
                        progress=min(95, current_progress)
                    )
                    
                    current_progress += 0.5  # 緩慢增加進度
                    
                elif event.type == "message_stop":
                    # 發送完成訊息
                    yield send_sse_data('complete', progress=100, message='記錄生成完成')
                    break
                    
    except Exception as e:
        logger.error(f"記錄生成過程發生錯誤: {str(e)}")
        yield send_sse_data('error', error=f'記錄生成失敗: {str(e)}')

def generate_treatment_plan_streaming(transcript, report_draft, selected_service_domains, social_worker_notes):
    """使用 Claude API 生成處遇計畫並串流回傳"""
    try:
        # 發送開始生成的訊息
        yield send_sse_data('progress', progress=10, message='準備生成處遇計畫...')
        
        # 建構 prompt
        prompt = build_treatment_prompt(transcript, report_draft, selected_service_domains, social_worker_notes)
        
        yield send_sse_data('progress', progress=20, message='正在請求 AI 生成處遇計畫...')
        
        # 調用 Claude API
        with claude_client.messages.stream(
            model="claude-4-sonnet-20250514",
            max_tokens=4000,
            temperature=0.3,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        ) as stream:
            
            current_progress = 30
            accumulated_text = ""
            
            for event in stream:
                if event.type == "content_block_delta":
                    text_chunk = event.delta.text
                    accumulated_text += text_chunk
                    
                    # 發送文字片段
                    yield send_sse_data(
                        'chunk',
                        text=text_chunk,
                        progress=min(95, current_progress)
                    )
                    
                    current_progress += 0.5  # 緩慢增加進度
                    
                elif event.type == "message_stop":
                    # 發送完成訊息
                    yield send_sse_data('complete', progress=100, message='處遇計畫生成完成')
                    break
                    
    except Exception as e:
        logger.error(f"處遇計畫生成過程發生錯誤: {str(e)}")
        yield send_sse_data('error', error=f'處遇計畫生成失敗: {str(e)}')

def transcribe_audio_streaming(audio_file_path, filename):
    """使用 OpenAI Whisper API 轉換音檔並串流回傳"""
    try:
        # 發送開始轉換的訊息
        yield send_sse_data('progress', progress=10, message='開始上傳音檔到 OpenAI...')
        
        # 打開音檔並發送到 OpenAI
        with open(audio_file_path, 'rb') as audio_file:
            # 發送進度更新
            yield send_sse_data('progress', progress=30, message='正在轉換音檔...')
            
            # 調用 OpenAI Whisper API
            transcript_response = openai_client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                response_format="verbose_json",  # 獲取更詳細的資訊
                language="zh"  # 指定中文，也可以設為 None 讓 AI 自動偵測
            )
            
            # 發送進度更新
            yield send_sse_data('progress', progress=70, message='解析轉換結果...')
            
            # 獲取轉換結果
            transcript_text = transcript_response.text
            
            # 模擬串流效果 - 將文字分段發送
            if transcript_text:
                # 將文字按句號分割
                sentences = transcript_text.replace('。', '。|').replace('！', '！|').replace('？', '？|').split('|')
                sentences = [s.strip() for s in sentences if s.strip()]
                
                progress_step = 20 / len(sentences) if sentences else 20
                current_progress = 70
                
                for i, sentence in enumerate(sentences):
                    current_progress += progress_step
                    
                    # 發送文字片段
                    yield send_sse_data(
                        'chunk', 
                        text=sentence + ('。' if not sentence.endswith(('。', '！', '？')) else ''),
                        progress=min(95, int(current_progress))
                    )
                    
                    # 添加小延遲模擬串流效果
                    time.sleep(0.2)
            else:
                yield send_sse_data('chunk', text='', progress=95)
            
            # 發送完成訊息
            yield send_sse_data('complete', progress=100, message='轉換完成')
            
    except Exception as e:
        logger.error(f"轉換過程發生錯誤: {str(e)}")
        yield send_sse_data('error', error=f'轉換失敗: {str(e)}')

@app.route('/api/transcribe', methods=['POST'])
def transcribe_audio():
    """音檔轉逐字稿 API"""
    try:
        # 檢查是否有檔案
        if 'audio' not in request.files:
            return jsonify({'error': '沒有提供音檔'}), 400
        
        audio_file = request.files['audio']
        
        # 檢查檔案名稱
        if audio_file.filename == '':
            return jsonify({'error': '沒有選擇檔案'}), 400
        
        # 檢查檔案格式
        if not allowed_file(audio_file.filename):
            return jsonify({
                'error': f'不支援的檔案格式。支援格式: {", ".join(ALLOWED_EXTENSIONS)}'
            }), 400
        
        # 檢查檔案大小
        file_size = get_file_size(audio_file)
        if file_size > MAX_FILE_SIZE:
            return jsonify({
                'error': f'檔案大小超過限制 ({MAX_FILE_SIZE // (1024*1024)}MB)'
            }), 400
        
        # 生成安全的檔案名稱
        filename = secure_filename(audio_file.filename)
        
        # 創建臨時檔案
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{filename.split('.')[-1]}") as tmp_file:
            audio_file.save(tmp_file.name)
            temp_file_path = tmp_file.name
        
        def generate():
            try:
                # 發送開始處理的訊息
                yield send_sse_data('progress', progress=5, message='檔案上傳成功，開始處理...')
                
                # 執行轉換並串流回傳
                for chunk in transcribe_audio_streaming(temp_file_path, filename):
                    yield chunk
                    
            except Exception as e:
                logger.error(f"串流過程發生錯誤: {str(e)}")
                yield send_sse_data('error', error=f'處理失敗: {str(e)}')
            finally:
                # 清理臨時檔案
                try:
                    os.unlink(temp_file_path)
                except:
                    pass
        
        # 回傳 SSE 響應
        return Response(
            generate(),
            mimetype='text/plain',
            headers={
                'Cache-Control': 'no-cache',
                'Connection': 'keep-alive',
                'Content-Type': 'text/event-stream',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Cache-Control'
            }
        )
        
    except Exception as e:
        logger.error(f"API 處理錯誤: {str(e)}")
        return jsonify({'error': f'伺服器錯誤: {str(e)}'}), 500

@app.route('/api/generate-report', methods=['POST'])
def generate_report():
    """生成記錄初稿 API"""
    try:
        # 獲取請求資料
        data = request.get_json()
        
        # 驗證必要欄位
        if not data:
            return jsonify({'error': '沒有提供請求資料'}), 400
        
        transcript = data.get('transcript', '').strip()
        if not transcript:
            return jsonify({'error': '逐字稿內容不能為空'}), 400
        
        social_worker_notes = data.get('socialWorkerNotes', '').strip()
        selected_sections = data.get('selectedSections', [])
        required_sections = data.get('requiredSections', [])
        
        logger.info(f"收到記錄生成請求 - 逐字稿長度: {len(transcript)}, 選擇段落: {len(selected_sections)}")
        
        def generate():
            try:
                # 發送開始處理的訊息
                yield send_sse_data('progress', progress=5, message='開始生成記錄...')
                
                # 執行記錄生成並串流回傳
                for chunk in generate_report_streaming(transcript, social_worker_notes, selected_sections, required_sections):
                    yield chunk
                    
            except Exception as e:
                logger.error(f"記錄生成串流過程發生錯誤: {str(e)}")
                yield send_sse_data('error', error=f'記錄生成失敗: {str(e)}')
        
        # 回傳 SSE 響應
        return Response(
            generate(),
            mimetype='text/plain',
            headers={
                'Cache-Control': 'no-cache',
                'Connection': 'keep-alive',
                'Content-Type': 'text/event-stream',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Cache-Control'
            }
        )
        
    except Exception as e:
        logger.error(f"API 處理錯誤: {str(e)}")
        return jsonify({'error': f'伺服器錯誤: {str(e)}'}), 500

@app.route('/api/generate-treatment-plan', methods=['POST'])
def generate_treatment_plan():
    """生成處遇計畫 API"""
    try:
        # 獲取請求資料
        data = request.get_json()
        
        # 驗證必要欄位
        if not data:
            return jsonify({'error': '沒有提供請求資料'}), 400
        
        # 獲取必要資料
        transcript = data.get('transcript', '').strip()
        report_draft = data.get('reportDraft', '').strip()
        selected_service_domains = data.get('selectedServiceDomains', [])
        social_worker_notes = data.get('socialWorkerNotes', '').strip()
        
        # 驗證必要欄位
        if not report_draft and not transcript:
            return jsonify({'error': '必須提供記錄初稿或逐字稿內容'}), 400
        
        if not selected_service_domains:
            return jsonify({'error': '必須至少選擇一個社工服務領域'}), 400
        
        logger.info(f"收到處遇計畫生成請求 - 記錄長度: {len(report_draft)}, 服務領域: {selected_service_domains}")
        
        def generate():
            try:
                # 發送開始處理的訊息
                yield send_sse_data('progress', progress=5, message='開始生成處遇計畫...')
                
                # 執行處遇計畫生成並串流回傳
                for chunk in generate_treatment_plan_streaming(transcript, report_draft, selected_service_domains, social_worker_notes):
                    yield chunk
                    
            except Exception as e:
                logger.error(f"處遇計畫生成串流過程發生錯誤: {str(e)}")
                yield send_sse_data('error', error=f'處遇計畫生成失敗: {str(e)}')
        
        # 回傳 SSE 響應
        return Response(
            generate(),
            mimetype='text/plain',
            headers={
                'Cache-Control': 'no-cache',
                'Connection': 'keep-alive',
                'Content-Type': 'text/event-stream',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Cache-Control'
            }
        )
        
    except Exception as e:
        logger.error(f"API 處理錯誤: {str(e)}")
        return jsonify({'error': f'伺服器錯誤: {str(e)}'}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """健康檢查端點"""
    return jsonify({
        'status': 'healthy',
        'service': 'social-work-report-generator',
        'timestamp': time.time(),
        'apis': ['transcribe', 'generate-report', 'generate-treatment-plan']
    })

@app.route('/api/supported-formats', methods=['GET'])
def get_supported_formats():
    """獲取支援的檔案格式"""
    return jsonify({
        'supported_formats': list(ALLOWED_EXTENSIONS),
        'max_file_size_mb': MAX_FILE_SIZE // (1024*1024)
    })

@app.errorhandler(413)
def too_large(e):
    """檔案太大錯誤處理"""
    return jsonify({
        'error': f'檔案大小超過限制 ({MAX_FILE_SIZE // (1024*1024)}MB)'
    }), 413

@app.errorhandler(400)
def bad_request(e):
    """錯誤請求處理"""
    return jsonify({'error': '錯誤的請求'}), 400

@app.errorhandler(500)
def internal_error(e):
    """內部伺服器錯誤處理"""
    return jsonify({'error': '內部伺服器錯誤'}), 500

if __name__ == '__main__':
    # 再次檢查 API 金鑰
    if not openai_api_key or not claude_api_key:
        logger.error("❌ 錯誤: API 金鑰未完整設置")
        logger.error("請檢查 .env 檔案是否存在且格式正確")
        exit(1)
    
    logger.info("🔑 API 金鑰驗證成功")
    logger.info("🚀 啟動 Flask 社工報告生成服務...")
    
    # 設置 Flask 配置
    app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE
    
    # 啟動應用
    app.run(
        host='0.0.0.0',
        port=5353,
        debug=True,
        threaded=True
    )