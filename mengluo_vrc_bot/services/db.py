import sqlite3

from mengluo_vrc_bot.config.path import DATA_PATH
from .log import logger

DATABASE_PATH = DATA_PATH / "database.db"

def init_db():
    """初始化数据库表（使用上下文管理器自动关闭连接）"""
    with sqlite3.connect(DATABASE_PATH) as conn:  # 上下文管理器自动关闭连接
        c = conn.cursor()  # 移除with语句，直接获取游标
        c.execute('''CREATE TABLE IF NOT EXISTS user_info
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      user_id TEXT NOT NULL UNIQUE,
                      vrc_id TEXT NOT NULL UNIQUE,
                      vrc_authorization TEXT,
                      vrc_cookie TEXT)''')
        c.close()  # 显式关闭游标（可选，连接关闭时会自动关闭游标）
        conn.commit()

async def get_db():
    """获取数据库连接（保持异步接口）"""
    return sqlite3.connect(DATABASE_PATH)

async def execute(sql, *args):
    """执行写操作（添加异常处理确保连接关闭）"""
    conn = None
    try:
        conn = await get_db()
        c = conn.cursor()  # 移除with语句，直接获取游标
        c.execute(sql, args)
        c.close()  # 显式关闭游标（可选）
        conn.commit()  # 提交事务
    except Exception as e:
        logger.error(f"执行SQL语句时发生错误: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()

async def fetchone(sql, *args):
    """执行读操作（添加异常处理确保连接关闭）"""
    conn = None
    try:
        conn = await get_db()
        c = conn.cursor()  # 移除with语句，直接获取游标
        c.execute(sql, args)
        result = c.fetchone()
        c.close()  # 显式关闭游标（可选）
        return result
    except Exception as e:
        logger.error(f"执行SQL语句时发生错误: {e}")
        return None
    finally:
        if conn:
            conn.close()