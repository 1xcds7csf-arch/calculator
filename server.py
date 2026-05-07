#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简易HTTP服务器 - 支持局域网访问的计算器应用
"""

import http.server
import socketserver
import socket
import os
import json
from urllib.parse import parse_qs, urlparse
from database import db
from decimal import Decimal

PORT = 8080

# 简单的会话存储（实际项目应使用 Redis 或其他会话存储）
active_sessions = {}

class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def _convert_decimal(self, obj):
        """将 Decimal 类型转换为 float"""
        if isinstance(obj, Decimal):
            return float(obj)
        raise TypeError(f"Object of type {type(obj)} is not JSON serializable")
    
    def end_headers(self):
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()
    
    def do_POST(self):
        parsed_path = urlparse(self.path)
        
        if parsed_path.path == '/api/calculate':
            self._handle_calculate()
        elif parsed_path.path == '/api/record':
            self._handle_save_record()
        elif parsed_path.path == '/api/operation-log':
            self._handle_save_operation_log()
        elif parsed_path.path == '/api/register':
            self._handle_register()
        elif parsed_path.path == '/api/login':
            self._handle_login()
        elif parsed_path.path == '/api/logout':
            self._handle_logout()
        elif parsed_path.path == '/api/upgrade-vip':
            self._handle_upgrade_vip()
        else:
            self.send_response(404)
            self.end_headers()
    
    def do_GET(self):
        parsed_path = urlparse(self.path)
        
        if parsed_path.path == '/api/records':
            self._handle_get_records()
        elif parsed_path.path == '/api/stats':
            self._handle_get_stats()
        elif parsed_path.path == '/api/operation-logs':
            self._handle_get_operation_logs()
        elif parsed_path.path == '/history':
            self.path = '/history.html'
            return super().do_GET()
        else:
            return super().do_GET()
    
    def _handle_calculate(self):
        """处理计算请求：执行计算并保存记录"""
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            num1 = data.get('num1')
            num2 = data.get('num2')
            operator = data.get('operator')
            client_ip = self.client_address[0]
            
            # 检查乘法和除法的权限
            if operator in ['*', '/']:
                # 从 Cookie 获取会话 ID
                cookies = self.headers.get('Cookie', '')
                session_id = None
                for cookie in cookies.split(';'):
                    if 'session_id' in cookie:
                        session_id = cookie.split('=')[1].strip()
                        break
                
                if not session_id or session_id not in active_sessions:
                    self.send_response(403)
                    self.send_header('Content-Type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({
                        'success': False,
                        'error': '需要登录才能使用乘法和除法运算',
                        'requireLogin': True
                    }).encode())
                    return
                
                # 检查除法需要VIP
                if operator == '/':
                    user_session = active_sessions[session_id]
                    if not user_session.get('is_vip', False):
                        self.send_response(403)
                        self.send_header('Content-Type', 'application/json')
                        self.end_headers()
                        self.wfile.write(json.dumps({
                            'success': False,
                            'error': '除法运算需要VIP权限，请升级VIP',
                            'requireVip': True
                        }).encode())
                        return
            
            # 执行计算
            result = None
            error = None
            
            if operator == '+':
                result = num1 + num2
            elif operator == '-':
                result = num1 - num2
            elif operator == '*':
                result = num1 * num2
            elif operator == '/':
                if num2 == 0:
                    error = "除数不能为零"
                else:
                    result = num1 / num2
            else:
                error = "无效的运算符"
            
            # 保存计算记录到数据库
            if result is not None:
                db.save_record(num1, num2, operator, result, client_ip)
                # 同时保存操作日志
                db.save_operation_log(num1, num2, operator, result, client_ip)
                
                # 格式化结果
                if isinstance(result, float) and result.is_integer():
                    result = int(result)
                
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({
                    'success': True,
                    'result': result,
                    'num1': num1,
                    'num2': num2,
                    'operator': operator
                }).encode())
            else:
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({
                    'success': False,
                    'error': error
                }).encode())
                
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'success': False, 'error': str(e)}).encode())
    
    def _handle_save_record(self):
        """保存计算记录（备用接口）"""
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            num1 = data.get('num1')
            num2 = data.get('num2')
            operator = data.get('operator')
            result = data.get('result')
            client_ip = self.client_address[0]
            
            success = db.save_record(num1, num2, operator, result, client_ip)
            
            self.send_response(200 if success else 500)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'success': success}).encode())
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'success': False, 'error': str(e)}).encode())
    
    def _handle_get_records(self):
        """获取计算记录"""
        try:
            parsed_path = urlparse(self.path)
            params = parse_qs(parsed_path.query)
            
            limit = int(params.get('limit', [100])[0])
            offset = int(params.get('offset', [0])[0])
            
            # 检查是否有筛选条件
            num1_filter = params.get('num1', [None])[0]
            num2_filter = params.get('num2', [None])[0]
            
            if num1_filter is not None or num2_filter is not None:
                num1 = float(num1_filter) if num1_filter else None
                num2 = float(num2_filter) if num2_filter else None
                records = db.get_records_by_numbers(num1=num1, num2=num2, limit=limit)
            else:
                records = db.get_records(limit=limit, offset=offset)
            
            # 转换 datetime 为字符串（SQLite 返回的已经是字符串）
            for record in records:
                if 'calc_time' in record and record['calc_time']:
                    # 如果已经是字符串则跳过，否则转换
                    if hasattr(record['calc_time'], 'strftime'):
                        record['calc_time'] = record['calc_time'].strftime('%Y-%m-%d %H:%M:%S')
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'success': True, 'data': records}).encode())
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'success': False, 'error': str(e)}).encode())
    
    def _handle_get_stats(self):
        """获取统计信息"""
        try:
            stats = db.get_stats()
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'success': True, 'data': stats}).encode())
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'success': False, 'error': str(e)}).encode())
    
    def _handle_save_operation_log(self):
        """保存操作日志"""
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            num1 = data.get('num1')
            num2 = data.get('num2')
            operator = data.get('operator')
            result = data.get('result')
            client_ip = self.client_address[0]
            
            success = db.save_operation_log(num1, num2, operator, result, client_ip)
            self.send_response(200 if success else 500)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'success': success}).encode())
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'success': False, 'error': str(e)}).encode())
    
    def _handle_get_operation_logs(self):
        """获取操作日志列表"""
        try:
            parsed_path = urlparse(self.path)
            params = parse_qs(parsed_path.query)
            
            limit = int(params.get('limit', [100])[0])
            offset = int(params.get('offset', [0])[0])
            
            logs = db.get_operation_logs(limit=limit, offset=offset)
            
            # 转换 datetime 为字符串
            for log in logs:
                if 'created_at' in log and log['created_at']:
                    if hasattr(log['created_at'], 'strftime'):
                        log['created_at'] = log['created_at'].strftime('%Y-%m-%d %H:%M:%S')
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'success': True, 'data': logs}, default=self._convert_decimal).encode())
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'success': False, 'error': str(e)}).encode())
    
    def _handle_register(self):
        """处理用户注册"""
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            username = data.get('username')
            password = data.get('password')
            
            if not username or not password:
                self.send_response(400)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({
                    'success': False,
                    'error': '用户名和密码不能为空'
                }).encode())
                return
            
            success = db.create_user(username, password)
            
            if success:
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({
                    'success': True,
                    'message': '注册成功'
                }).encode())
            else:
                self.send_response(400)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({
                    'success': False,
                    'error': '用户名已存在或注册失败'
                }).encode())
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'success': False, 'error': str(e)}).encode())
    
    def _handle_login(self):
        """处理用户登录"""
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            username = data.get('username')
            password = data.get('password')
            
            user = db.verify_user(username, password)
            
            if user:
                # 创建会话
                import uuid
                session_id = str(uuid.uuid4())
                active_sessions[session_id] = {
                    'user_id': user['id'],
                    'username': user['username'],
                    'is_vip': bool(user['is_vip'])
                }
                
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Set-Cookie', f'session_id={session_id}; Path=/; HttpOnly')
                self.end_headers()
                self.wfile.write(json.dumps({
                    'success': True,
                    'message': '登录成功',
                    'username': user['username'],
                    'isVip': bool(user['is_vip'])
                }).encode())
            else:
                self.send_response(401)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({
                    'success': False,
                    'error': '用户名或密码错误'
                }).encode())
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'success': False, 'error': str(e)}).encode())
    
    def _handle_logout(self):
        """处理用户登出"""
        try:
            cookies = self.headers.get('Cookie', '')
            session_id = None
            for cookie in cookies.split(';'):
                if 'session_id' in cookie:
                    session_id = cookie.split('=')[1].strip()
                    break
            
            if session_id and session_id in active_sessions:
                del active_sessions[session_id]
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Set-Cookie', 'session_id=; Path=/; HttpOnly; Max-Age=0')
            self.end_headers()
            self.wfile.write(json.dumps({
                'success': True,
                'message': '登出成功'
            }).encode())
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'success': False, 'error': str(e)}).encode())
    
    def _handle_upgrade_vip(self):
        """处理VIP升级"""
        try:
            cookies = self.headers.get('Cookie', '')
            session_id = None
            for cookie in cookies.split(';'):
                if 'session_id' in cookie:
                    session_id = cookie.split('=')[1].strip()
                    break
            
            if not session_id or session_id not in active_sessions:
                self.send_response(401)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({
                    'success': False,
                    'error': '请先登录'
                }).encode())
                return
            
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            phone = data.get('phone')
            birthday = data.get('birthday')
            gender = data.get('gender')
            email = data.get('email')
            membership_type = data.get('membership_type', 'standard')
            
            if not phone or not birthday or not gender:
                self.send_response(400)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({
                    'success': False,
                    'error': '请填写完整的注册信息'
                }).encode())
                return
            
            user_session = active_sessions[session_id]
            user_id = user_session['user_id']
            
            success = db.upgrade_to_vip(user_id, phone, birthday, gender, email, membership_type)
            
            if success:
                active_sessions[session_id]['is_vip'] = True
                
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({
                    'success': True,
                    'message': '升级VIP成功'
                }).encode())
            else:
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({
                    'success': False,
                    'error': '升级VIP失败'
                }).encode())
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'success': False, 'error': str(e)}).encode())
    
    def log_message(self, format, *args):
        # 自定义日志格式，显示访问信息
        print(f"[{self.log_date_time_string()}] {self.address_string()} - {format % args}")

def get_local_ip():
    """获取本机局域网IP地址"""
    try:
        # 创建一个UDP套接字来获取本地IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception:
        return "127.0.0.1"

def main():
    # 切换到脚本所在目录
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    local_ip = get_local_ip()
    
    with socketserver.TCPServer(("0.0.0.0", PORT), MyHTTPRequestHandler) as httpd:
        print("=" * 60)
        print("[INFO] 计算器服务器已启动！")
        print("=" * 60)
        print(f"\n本机访问地址: http://localhost:{PORT}")
        print(f"局域网访问地址: http://{local_ip}:{PORT}")
        print(f"\n服务目录: {os.getcwd()}")
        print("\n按 Ctrl+C 停止服务器")
        print("=" * 60)
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n\n👋 服务器已停止")

if __name__ == "__main__":
    main()
