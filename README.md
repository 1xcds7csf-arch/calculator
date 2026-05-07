# 🧮 计算器应用

一个支持局域网访问的简易计算器应用，提供用户认证、运算记录、VIP权限等功能。

## 🎯 功能特性

### 核心功能
- **基础运算**：支持加法、减法运算，无需登录即可使用
- **高级运算**：支持乘法、除法运算，需要用户登录
- **VIP专属**：除法运算仅限VIP用户使用
- **运算记录**：自动保存用户的运算历史记录
- **操作日志**：记录所有用户操作，便于审计

### 用户系统
- **用户注册**：支持新用户注册账号
- **用户登录**：支持账号密码登录
- **VIP升级**：填写个人信息并选择会员类型升级为VIP会员
- **会话管理**：自动管理用户登录会话

### VIP会员类型
| 会员类型 | 价格 | 权益 |
|----------|------|------|
| ⭐ 标准VIP | 免费 | 基础除法运算 |
| 💎 高级VIP | ¥9.9/月 | 高级运算功能、优先技术支持 |
| 🏢 企业VIP | ¥99/月 | 全部功能、专属客服、API接入 |

### 界面特性
- 简洁美观的深色主题界面
- 响应式设计，支持不同屏幕尺寸
- 实时显示运算历史和结果
- 支持键盘快捷操作
- VIP注册模态框支持滚动，内容完整显示

## 🛠 技术栈

### 后端
| 技术 | 版本 | 说明 |
|------|------|------|
| Python | 3.x | 服务器端编程语言 |
| http.server | 内置 | Python标准库HTTP服务器 |
| PyMySQL | - | MySQL数据库驱动 |
| MySQL | 5.7+ | 数据库管理系统 |

### 前端
| 技术 | 说明 |
|------|------|
| HTML5 | 页面结构 |
| CSS3 | 样式设计 |
| JavaScript | 交互逻辑 |
| Fetch API | 异步HTTP请求 |

## 🌐 API接口

### 1. 计算接口

**POST** `/api/calculate`

执行数学运算

**请求体**：
```json
{
    "num1": 10,
    "num2": 5,
    "operator": "+"
}
```

**参数说明**：
| 参数 | 类型 | 说明 |
|------|------|------|
| num1 | number | 第一个操作数 |
| num2 | number | 第二个操作数 |
| operator | string | 运算符：`+`, `-`, `*`, `/` |

**响应示例**：
```json
{
    "success": true,
    "result": 15
}
```

**权限说明**：
- `+`, `-`：无需登录
- `*`：需要登录
- `/`：需要VIP权限

---

### 2. 用户注册

**POST** `/api/register`

注册新用户

**请求体**：
```json
{
    "username": "username",
    "password": "password"
}
```

**响应示例**：
```json
{
    "success": true,
    "message": "注册成功"
}
```

---

### 3. 用户登录

**POST** `/api/login`

用户登录

**请求体**：
```json
{
    "username": "username",
    "password": "password"
}
```

**响应示例**：
```json
{
    "success": true,
    "message": "登录成功",
    "is_vip": false
}
```

---

### 4. 用户登出

**POST** `/api/logout`

用户登出

**响应示例**：
```json
{
    "success": true,
    "message": "登出成功"
}
```

---

### 5. 升级VIP

**POST** `/api/upgrade-vip`

升级为VIP会员

**请求体**：
```json
{
    "phone": "18200553708",
    "birthday": "2010-06-25",
    "gender": "女",
    "email": "user@example.com",
    "membership_type": "standard"
}
```

**参数说明**：
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| phone | string | ✅ | 手机号 |
| birthday | string | ✅ | 生日（YYYY-MM-DD） |
| gender | string | ✅ | 性别（男/女/其他） |
| email | string | ❌ | 邮箱地址（选填） |
| membership_type | string | ❌ | 会员类型（standard/premium/enterprise），默认standard |

**响应示例**：
```json
{
    "success": true,
    "message": "升级VIP成功"
}
```

---

### 6. 保存记录

**POST** `/api/record`

保存运算记录（内部使用）

---

### 7. 保存操作日志

**POST** `/api/operation-log`

保存操作日志（内部使用）

---

### 8. 统计接口

**GET** `/api/stats`

获取运算统计信息

**响应示例**：
```json
{
    "success": true,
    "data": {
        "total_records": 20,
        "operator_stats": [
            {"operator": "*", "count": 10},
            {"operator": "+", "count": 5}
        ]
    }
}
```

## 📖 使用说明

### 快速开始

1. **启动服务器**
```bash
python server.py
```

2. **访问应用**
- 本机访问：`http://localhost:8080`
- 局域网访问：`http://{本机IP}:8080`

### 操作指南

1. **基础运算**
   - 直接点击数字按钮输入数字
   - 点击运算符选择运算类型
   - 点击 `=` 执行计算

2. **键盘支持**
   - `0-9`：输入数字
   - `+`, `-`, `*`, `/`：选择运算符
   - `Enter` 或 `=`：执行计算
   - `Backspace`：删除最后一位
   - `Escape`：清空所有

3. **登录/注册**
   - 点击右上角「登录」按钮
   - 选择「注册」创建新账号
   - 登录后可使用乘法运算

4. **升级VIP**
   - 登录后点击「升级VIP」按钮
   - 填写手机号、性别、生日信息
   - 选择会员类型（标准VIP/高级VIP/企业VIP）
   - 阅读并同意服务协议和隐私政策
   - 提交后即可使用除法运算

## 🔐 权限说明

| 功能 | 未登录 | 已登录 | VIP用户 |
|------|--------|--------|---------|
| 加法运算 | ✅ | ✅ | ✅ |
| 减法运算 | ✅ | ✅ | ✅ |
| 乘法运算 | ❌ | ✅ | ✅ |
| 除法运算 | ❌ | ❌ | ✅ |
| 查看运算记录 | ❌ | ✅ | ✅ |

## ⚙ 配置说明

### 数据库配置

在 `database.py` 中配置数据库连接：

```python
DB_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'calc_db',
    'password': 'calc_db',
    'database': 'calc_db',
    'charset': 'utf8mb4'
}
```

### 服务器配置

在 `server.py` 中配置端口：

```python
PORT = 8080
```

### MySQL数据库准备

1. 创建数据库：
```sql
CREATE DATABASE calc_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

2. 创建用户并授权：
```sql
CREATE USER 'calc_db'@'localhost' IDENTIFIED BY 'calc_db';
GRANT ALL PRIVILEGES ON calc_db.* TO 'calc_db'@'localhost';
FLUSH PRIVILEGES;
```

## 📁 项目结构

```
calculator/
├── server.py          # 后端HTTP服务器
├── database.py        # 数据库操作模块
├── index.html         # 主页面（包含VIP注册模态框）
├── history.html       # 历史记录页面
└── README.md          # 项目说明文档
```

## 🚀 启动方式

### 开发环境

```bash
# 安装依赖
pip install pymysql

# 启动服务器
python server.py
```

### 运行状态

服务器启动后会显示：
- 服务启动成功提示
- 本机访问地址
- 局域网访问地址

## 📝 更新日志

### v1.1.0
- 添加VIP会员类型选择（标准/高级/企业）
- 添加服务协议和隐私政策模态框
- 优化VIP注册界面UI，支持滚动显示完整内容
- 添加会员类型标签式权益展示
- 更新数据库支持会员类型字段

### v1.0.0
- 基础计算器功能（加、减、乘、除）
- 用户注册/登录系统
- VIP会员升级功能
- 运算记录保存
- 操作日志记录
- 局域网访问支持

## 📄 许可证

MIT License
