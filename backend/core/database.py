# ================================
# 2. 數據庫配置 - core/database.py
# ================================

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
import os
from contextlib import contextmanager
import logging

logger = logging.getLogger(__name__)

# 數據庫配置
DATABASE_URL = os.getenv(
    'DATABASE_URL', 
    'postgresql://yining_juan@127.0.0.1:5432/social_work_logs_db'
)

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=10,
    pool_recycle=3600,
    pool_pre_ping=True,
    max_overflow=5
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db() -> Session:
    """獲取數據庫會話"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@contextmanager
def get_db_context():
    """用於非依賴注入場景的數據庫會話"""
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

# 創建表格
def create_tables():
    """創建所有表格"""
    from models.api_usage_log import Base
    Base.metadata.create_all(bind=engine)