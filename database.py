#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库模块 - 使用 MySQL 管理计算记录的存储和查询
"""

import pymysql
import json
import os
from datetime import datetime
from contextlib import contextmanager

# MySQL 数据库配置
DB_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'calc_db',
    'password': 'calc_db',
    'database': 'calc_db',
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor
}

class Database:
    def __init__(self):
        self.db_config = DB_CONFIG
        self._create_tables()
    
    def _create_tables(self):
        """创建计算记录表和操作日志表"""
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cursor:
                    # 创建计算记录表
                    sql = """
                    CREATE TABLE IF NOT EXISTS calculation_records (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        num1 DECIMAL(10, 2) NOT NULL,
                        num2 DECIMAL(10, 2) NOT NULL,
                        operator VARCHAR(10) NOT NULL,
                        result DECIMAL(10, 2) NOT NULL,
                        calc_time DATETIME DEFAULT CURRENT_TIMESTAMP,
                        client_ip VARCHAR(45)
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
                    """
                    cursor.execute(sql)
                    
                    # 创建索引（MySQL不支持IF NOT EXISTS，需要捕获异常）
                    try:
                        cursor.execute("CREATE INDEX idx_calc_time ON calculation_records(calc_time)")
                    except:
                        pass  # 索引已存在
                    
                    try:
                        cursor.execute("CREATE INDEX idx_num1 ON calculation_records(num1)")
                    except:
                        pass
                    
                    try:
                        cursor.execute("CREATE INDEX idx_num2 ON calculation_records(num2)")
                    except:
                        pass
                    
                    # 创建操作日志表
                    sql_log = """
                    CREATE TABLE IF NOT EXISTS operation_log (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        num1 DECIMAL(10, 2),
                        num2 DECIMAL(10, 2),
                        operator VARCHAR(10),
                        result DECIMAL(10, 2),
                        client_ip VARCHAR(45),
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
                    """
                    cursor.execute(sql_log)
                    
                    # 创建用户表
                    sql_users = """
                    CREATE TABLE IF NOT EXISTS users (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        username VARCHAR(50) NOT NULL UNIQUE,
                        password VARCHAR(100) NOT NULL,
                        is_vip TINYINT(1) DEFAULT 0,
                        phone VARCHAR(20),
                        birthday DATE,
                        gender VARCHAR(10),
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
                    """
                    cursor.execute(sql_users)
                    
                    conn.commit()
                    print("[INFO] 数据库表创建成功")
        except Exception as e:
            print(f"创建表失败: {e}")
    
    @contextmanager
    def _get_connection(self):
        """获取数据库连接"""
        conn = None
        try:
            conn = pymysql.connect(**self.db_config)
            yield conn
        except Exception as e:
            if conn:
                conn.rollback()
            raise e
        finally:
            if conn:
                conn.close()
    
    def save_record(self, num1, num2, operator, result, client_ip=None):
        """保存计算记录"""
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cursor:
                    sql = """
                    INSERT INTO calculation_records (num1, num2, operator, result, calc_time, client_ip)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    """
                    cursor.execute(sql, (num1, num2, operator, result, datetime.now(), client_ip))
                    conn.commit()
                    return True
        except Exception as e:
            print(f"保存记录失败: {e}")
            return False
    
    def get_records(self, limit=100, offset=0):
        """获取计算记录列表"""
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cursor:
                    sql = """
                    SELECT id, num1, num2, operator, result, calc_time, client_ip
                    FROM calculation_records
                    ORDER BY calc_time DESC
                    LIMIT %s OFFSET %s
                    """
                    cursor.execute(sql, (limit, offset))
                    rows = cursor.fetchall()
                    return rows
        except Exception as e:
            print(f"查询记录失败: {e}")
            return []
    
    def get_records_by_numbers(self, num1=None, num2=None, limit=100):
        """根据数字查询计算记录"""
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cursor:
                    conditions = []
                    params = []
                    
                    if num1 is not None:
                        conditions.append("num1 = %s")
                        params.append(num1)
                    if num2 is not None:
                        conditions.append("num2 = %s")
                        params.append(num2)
                    
                    where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""
                    
                    sql = f"""
                    SELECT id, num1, num2, operator, result, calc_time, client_ip
                    FROM calculation_records
                    {where_clause}
                    ORDER BY calc_time DESC
                    LIMIT %s
                    """
                    params.append(limit)
                    cursor.execute(sql, params)
                    rows = cursor.fetchall()
                    return rows
        except Exception as e:
            print(f"查询记录失败: {e}")
            return []
    
    def get_stats(self):
        """获取统计信息"""
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT COUNT(*) as total FROM calculation_records")
                    total = cursor.fetchone()['total']
                    
                    cursor.execute("""
                        SELECT operator, COUNT(*) as count 
                        FROM calculation_records 
                        GROUP BY operator
                    """)
                    operator_stats = cursor.fetchall()
                    
                    return {
                        'total_records': total,
                        'operator_stats': operator_stats
                    }
        except Exception as e:
            print(f"获取统计失败: {e}")
            return {'total_records': 0, 'operator_stats': []}
    
    def save_operation_log(self, num1=None, num2=None, operator=None, result=None, client_ip=None):
        """保存操作日志记录"""
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cursor:
                    sql = """
                    INSERT INTO operation_log (num1, num2, operator, result, client_ip, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    """
                    cursor.execute(sql, (num1, num2, operator, result, client_ip, datetime.now()))
                    conn.commit()
                    return True
        except Exception as e:
            print(f"保存操作日志失败: {e}")
            return False
    
    def get_operation_logs(self, limit=100, offset=0):
        """获取操作日志列表"""
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cursor:
                    sql = """
                    SELECT id, num1, num2, operator, result, client_ip, created_at
                    FROM operation_log
                    ORDER BY created_at DESC
                    LIMIT %s OFFSET %s
                    """
                    cursor.execute(sql, (limit, offset))
                    rows = cursor.fetchall()
                    return rows
        except Exception as e:
            print(f"查询操作日志失败: {e}")
            return []
    
    def create_user(self, username, password):
        """创建新用户"""
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cursor:
                    sql = """
                    INSERT INTO users (username, password)
                    VALUES (%s, %s)
                    """
                    cursor.execute(sql, (username, password))
                    conn.commit()
                    return True
        except Exception as e:
            print(f"创建用户失败: {e}")
            return False
    
    def verify_user(self, username, password):
        """验证用户登录"""
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cursor:
                    sql = """
                    SELECT id, username, is_vip FROM users
                    WHERE username = %s AND password = %s
                    """
                    cursor.execute(sql, (username, password))
                    user = cursor.fetchone()
                    return user
        except Exception as e:
            print(f"验证用户失败: {e}")
            return None
    
    def upgrade_to_vip(self, user_id, phone=None, birthday=None, gender=None):
        """升级用户为VIP"""
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cursor:
                    sql = """
                    UPDATE users SET is_vip = 1, phone = %s, birthday = %s, gender = %s WHERE id = %s
                    """
                    cursor.execute(sql, (phone, birthday, gender, user_id))
                    conn.commit()
                    return True
        except Exception as e:
            print(f"升级VIP失败: {e}")
            return False

# 全局数据库实例
db = Database()

if __name__ == '__main__':
    # 测试
    print("正在测试 MySQL 数据库连接...")
    try:
        db.save_record(10, 5, '+', 15, '127.0.0.1')
        print("[OK] 记录保存成功")
        records = db.get_records(limit=10)
        print(f"[OK] 查询到 {len(records)} 条记录")
        for r in records:
            print(r)
        
        db.save_operation_log()
        print("[OK] 操作日志保存成功")
        logs = db.get_operation_logs(limit=10)
        print(f"[OK] 查询到 {len(logs)} 条操作日志")
        for log in logs:
            print(log)
    except Exception as e:
        print(f"[ERROR] 测试失败: {e}")
