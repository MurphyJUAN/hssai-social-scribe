# create_schema_and_tables.py
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import sys
from datetime import datetime, timedelta
import json
import random

def create_schema_and_database():
    """創建數據庫、Schema 和表"""
    
    # 數據庫配置 - 請修改為你的實際配置
    DB_CONFIG = {
        'host': 'localhost',
        'port': 5432,
        'user': 'yining_juan',  # 替換為你的 PostgreSQL 用戶名
        'password': ''  # 替換為你的 PostgreSQL 密碼
    }
    
    DATABASE_NAME = 'social_work_logs_db'
    SCHEMA_NAME = 'social_work'
    
    try:
        # 1. 先確保數據庫存在
        print("正在連接到 PostgreSQL 服務器...")
        conn = psycopg2.connect(
            host=DB_CONFIG['host'],
            port=DB_CONFIG['port'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password'],
            database='postgres'  # 連接到默認數據庫
        )
        
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # 檢查數據庫是否已存在
        cursor.execute(
            "SELECT 1 FROM pg_catalog.pg_database WHERE datname = %s", 
            (DATABASE_NAME,)
        )
        exists = cursor.fetchone()
        
        if not exists:
            print(f"正在創建數據庫 '{DATABASE_NAME}'...")
            cursor.execute(f'CREATE DATABASE "{DATABASE_NAME}"')
            print(f"數據庫 '{DATABASE_NAME}' 創建成功！")
        else:
            print(f"數據庫 '{DATABASE_NAME}' 已存在")
        
        cursor.close()
        conn.close()
        
        # 2. 連接到目標數據庫並創建 schema
        print(f"正在連接到數據庫 '{DATABASE_NAME}'...")
        conn = psycopg2.connect(
            host=DB_CONFIG['host'],
            port=DB_CONFIG['port'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password'],
            database=DATABASE_NAME
        )
        
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # 檢查 schema 是否已存在
        cursor.execute(
            "SELECT 1 FROM information_schema.schemata WHERE schema_name = %s", 
            (SCHEMA_NAME,)
        )
        schema_exists = cursor.fetchone()
        
        if not schema_exists:
            print(f"正在創建 schema '{SCHEMA_NAME}'...")
            cursor.execute(f'CREATE SCHEMA "{SCHEMA_NAME}"')
            print(f"Schema '{SCHEMA_NAME}' 創建成功！")
        else:
            print(f"Schema '{SCHEMA_NAME}' 已存在")
        
        # 3. 創建表
        print("正在創建數據表...")
        create_table_sql = f"""
        CREATE TABLE IF NOT EXISTS {SCHEMA_NAME}.api_usage_logs (
            id SERIAL NOT NULL,
            timestamp TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
            ip VARCHAR(45) NOT NULL,
            endpoint VARCHAR(255) NOT NULL,
            method VARCHAR(10) NOT NULL,
            model_used VARCHAR(50),
            file_size INTEGER,
            processing_time INTEGER,
            success VARCHAR(10) NOT NULL,
            error_message TEXT,
            data_payload JSON,
            user_agent TEXT,
            PRIMARY KEY (id)
        );
        
        -- 創建索引以提高查詢性能
        CREATE INDEX IF NOT EXISTS idx_api_usage_logs_timestamp 
        ON {SCHEMA_NAME}.api_usage_logs(timestamp);
        
        CREATE INDEX IF NOT EXISTS idx_api_usage_logs_endpoint 
        ON {SCHEMA_NAME}.api_usage_logs(endpoint);
        
        CREATE INDEX IF NOT EXISTS idx_api_usage_logs_success 
        ON {SCHEMA_NAME}.api_usage_logs(success);
        
        CREATE INDEX IF NOT EXISTS idx_api_usage_logs_model_used 
        ON {SCHEMA_NAME}.api_usage_logs(model_used);
        """
        
        cursor.execute(create_table_sql)
        print("數據表和索引創建成功！")
        
        # 4. 驗證創建結果
        cursor.execute(f"""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_schema = '{SCHEMA_NAME}' AND table_name = 'api_usage_logs'
            ORDER BY ordinal_position
        """)
        columns = cursor.fetchall()
        
        print(f"\n表 '{SCHEMA_NAME}.api_usage_logs' 的結構：")
        for col_name, data_type, is_nullable in columns:
            print(f"  - {col_name}: {data_type} ({'NULL' if is_nullable == 'YES' else 'NOT NULL'})")
        
        cursor.close()
        conn.close()
        
        return True
        
    except psycopg2.Error as e:
        print(f"PostgreSQL 錯誤: {e}")
        return False
    except Exception as e:
        print(f"未知錯誤: {e}")
        return False

def insert_sample_data():
    """插入示例數據"""
    
    DB_CONFIG = {
        'host': 'localhost',
        'port': 5432,
        'user': 'yining_juan',  # 替換為你的實際配置
        'password': ''
    }
    
    DATABASE_NAME = 'social_work_logs_db'
    SCHEMA_NAME = 'social_work'
    
    # 生成示例數據
    endpoints = [
        '/backend/transcribe',
        '/backend/generate-report', 
        '/backend/generate-treatment-plan'
    ]
    
    models = ['whisper-1', 'gpt-4', 'gpt-3.5-turbo', 'claude-3']
    methods = ['POST', 'GET']
    success_statuses = ['success', 'error']
    ips = ['127.0.0.1', '192.168.1.100', '10.0.0.5', '172.16.0.10']
    
    sample_data = []
    base_time = datetime.now() - timedelta(days=30)
    
    for i in range(100):  # 生成100條示例記錄
        timestamp = base_time + timedelta(
            days=random.randint(0, 30),
            hours=random.randint(0, 23),
            minutes=random.randint(0, 59)
        )
        
        endpoint = random.choice(endpoints)
        is_success = random.choice([True, True, True, False])  # 75% 成功率
        
        record = (
            timestamp,
            random.choice(ips),
            endpoint,
            'POST' if endpoint != '/backend/health' else 'GET',
            random.choice(models) if endpoint.startswith('/backend') else None,
            random.randint(1024, 5242880) if endpoint != '/backend/health' else None,  # 1KB - 5MB
            random.randint(100, 5000) if is_success else random.randint(3000, 10000),  # 處理時間
            'success' if is_success else 'error',
            None if is_success else random.choice([
                'Timeout error',
                'Model overloaded',
                'Invalid input format',
                'Authentication failed',
                'Rate limit exceeded'
            ]),
            json.dumps({
                'request_id': f'req_{i:06d}',
                'client_version': f'1.{random.randint(0, 5)}.{random.randint(0, 10)}',
                'feature_flags': ['analytics', 'new_ui'] if random.random() > 0.5 else ['analytics']
            }),
            f'Mozilla/5.0 (compatible; AnalyticsBot/1.0; +http://example.com/bot)'
        )
        sample_data.append(record)
    
    try:
        print("正在插入示例數據...")
        conn = psycopg2.connect(
            host=DB_CONFIG['host'],
            port=DB_CONFIG['port'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password'],
            database=DATABASE_NAME
        )
        
        cursor = conn.cursor()
        
        # 檢查是否已有數據
        cursor.execute(f"SELECT COUNT(*) FROM {SCHEMA_NAME}.api_usage_logs")
        count = cursor.fetchone()[0]
        
        if count > 0:
            print(f"表中已有 {count} 條記錄")
            user_input = input("是否要清空現有數據並插入新的示例數據？(y/N): ").strip().lower()
            if user_input in ['y', 'yes']:
                cursor.execute(f"TRUNCATE TABLE {SCHEMA_NAME}.api_usage_logs RESTART IDENTITY")
                print("已清空現有數據")
            else:
                print("保留現有數據，跳過插入")
                cursor.close()
                conn.close()
                return True
        
        # 插入示例數據
        insert_sql = f"""
            INSERT INTO {SCHEMA_NAME}.api_usage_logs 
            (timestamp, ip, endpoint, method, model_used, file_size, processing_time, 
             success, error_message, data_payload, user_agent)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        cursor.executemany(insert_sql, sample_data)
        conn.commit()
        
        print(f"成功插入 {len(sample_data)} 條示例數據")
        
        # 顯示一些統計信息
        cursor.execute(f"""
            SELECT 
                endpoint,
                COUNT(*) as request_count,
                AVG(processing_time) as avg_processing_time,
                SUM(CASE WHEN success = 'success' THEN 1 ELSE 0 END) * 100.0 / COUNT(*) as success_rate
            FROM {SCHEMA_NAME}.api_usage_logs 
            GROUP BY endpoint
            ORDER BY request_count DESC
        """)
        
        stats = cursor.fetchall()
        print(f"\n📊 數據統計：")
        for endpoint, count, avg_time, success_rate in stats:
            print(f"  {endpoint}: {count}次請求, 平均{avg_time:.1f}ms, 成功率{success_rate:.1f}%")
        
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"插入示例數據時發生錯誤: {e}")
        return False

def test_connection():
    """測試數據庫連接和查詢"""
    
    DB_CONFIG = {
        'host': 'localhost',
        'port': 5432,
        'user': 'yining_juan',
        'password': ''
    }
    
    DATABASE_NAME = 'social_work_logs_db'
    SCHEMA_NAME = 'social_work'
    
    try:
        print("正在測試數據庫連接...")
        conn = psycopg2.connect(
            host=DB_CONFIG['host'],
            port=DB_CONFIG['port'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password'],
            database=DATABASE_NAME
        )
        
        cursor = conn.cursor()
        
        # 測試查詢
        cursor.execute(f"""
            SELECT COUNT(*) as total_records,
                   COUNT(DISTINCT ip) as unique_ips,
                   MIN(timestamp) as earliest_record,
                   MAX(timestamp) as latest_record
            FROM {SCHEMA_NAME}.api_usage_logs
        """)
        
        result = cursor.fetchone()
        total, unique_ips, earliest, latest = result
        
        print(f"✅ 連接測試成功！")
        print(f"📈 總記錄數: {total}")
        print(f"🌐 唯一IP數: {unique_ips}")
        print(f"📅 記錄時間範圍: {earliest} 到 {latest}")
        
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"❌ 連接測試失敗: {e}")
        return False

if __name__ == "__main__":
    print("=== Social Work Analytics 數據庫初始化 ===\n")
    
    print("⚠️  請先修改腳本中的數據庫配置信息！")
    print("需要修改: DB_CONFIG 中的 user 和 password\n")
    
    user_input = input("確認已修改配置？繼續執行？(y/N): ").strip().lower()
    if user_input not in ['y', 'yes']:
        print("已取消執行")
        sys.exit(0)
    
    # 步驟 1: 創建數據庫和 Schema
    if create_schema_and_database():
        print("✅ 數據庫、Schema 和表創建完成\n")
        
        # 步驟 2: 插入示例數據
        user_input = input("是否要插入示例數據用於測試？(y/N): ").strip().lower()
        if user_input in ['y', 'yes']:
            if insert_sample_data():
                print("✅ 示例數據插入完成\n")
            else:
                print("❌ 示例數據插入失敗\n")
        
        # 步驟 3: 測試連接
        if test_connection():
            print("\n🎉 數據庫初始化完成！現在可以啟動你的 FastAPI 應用了。")
            print("\n💡 提示：請確保你的 FastAPI 應用中的數據庫連接字符串正確：")
            print("DATABASE_URL = 'postgresql://username:password@localhost:5432/social_work_logs_db'")
        else:
            print("❌ 連接測試失敗")
            sys.exit(1)
    else:
        print("❌ 數據庫初始化失敗")
        sys.exit(1)