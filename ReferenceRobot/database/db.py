"""
数据库模块
用于保存和检索机器人操作的历史记录
"""

import sqlite3
import json
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).parent / 'reference_bot.db'

def init_db():
    """初始化数据库"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 创建历史记录表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        operation_type TEXT NOT NULL,
        input_data TEXT NOT NULL,
        result_data TEXT NOT NULL
    )
    ''')
    
    # 创建索引以提高查询性能
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_timestamp ON history(timestamp)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_operation_type ON history(operation_type)')
    
    conn.commit()
    conn.close()

def save_result(operation_type, input_data, result_data=None):
    """
    保存操作结果到数据库
    
    Args:
        operation_type: 操作类型（weather, currency, translation, calculator, unit_conversion）
        input_data: 输入数据（字典格式）
        result_data: 结果数据（字典格式）
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 如果result_data为None，使用input_data作为结果
    if result_data is None:
        result_data = input_data
    
    cursor.execute('''
    INSERT INTO history (operation_type, input_data, result_data)
    VALUES (?, ?, ?)
    ''', (
        operation_type,
        json.dumps(input_data, ensure_ascii=False),
        json.dumps(result_data, ensure_ascii=False)
    ))
    
    conn.commit()
    conn.close()

def get_history(limit=50, operation_type=None):
    """
    获取历史记录
    
    Args:
        limit: 返回的记录数量限制
        operation_type: 可选的过滤条件，指定操作类型
    
    Returns:
        历史记录列表
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    query = 'SELECT * FROM history'
    params = []
    
    if operation_type:
        query += ' WHERE operation_type = ?'
        params.append(operation_type)
    
    query += ' ORDER BY timestamp DESC LIMIT ?'
    params.append(limit)
    
    cursor.execute(query, params)
    rows = cursor.fetchall()
    
    history = []
    for row in rows:
        history.append({
            'id': row['id'],
            'timestamp': row['timestamp'],
            'operation_type': row['operation_type'],
            'input': json.loads(row['input_data']),
            'result': json.loads(row['result_data'])
        })
    
    conn.close()
    return history

def clear_history():
    """清空历史记录"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('DELETE FROM history')
    cursor.execute('VACUUM')  # 清理数据库空间
    
    conn.commit()
    conn.close()

def get_statistics():
    """获取使用统计"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 获取总操作次数
    cursor.execute('SELECT COUNT(*) FROM history')
    total_operations = cursor.fetchone()[0]
    
    # 获取各类型操作次数
    cursor.execute('''
    SELECT operation_type, COUNT(*) as count 
    FROM history 
    GROUP BY operation_type 
    ORDER BY count DESC
    ''')
    type_counts = cursor.fetchall()
    
    # 获取最近7天的使用情况
    cursor.execute('''
    SELECT DATE(timestamp) as date, COUNT(*) as count
    FROM history
    WHERE timestamp >= datetime('now', '-7 days')
    GROUP BY DATE(timestamp)
    ORDER BY date DESC
    ''')
    weekly_usage = cursor.fetchall()
    
    conn.close()
    
    return {
        'total_operations': total_operations,
        'type_counts': dict(type_counts),
        'weekly_usage': dict(weekly_usage) if weekly_usage else {}
    }
