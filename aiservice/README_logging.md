# AI 对话日志记录系统

## 概述

这个增强的日志记录系统可以完整记录 AI 对话的全过程，包括：
- 所有 API 请求和响应的完整内容
- 工具调用的参数和结果
- 模型的消息和响应
- 会话的完整时间线

## 主要功能

### 1. 自动日志记录
每次调用 `run_agent()` 时，系统会自动：
- 创建唯一的会话 ID
- 记录所有请求和响应到文件
- 在控制台显示详细的调试信息
- 在返回结果中包含日志文件路径

### 2. 日志文件位置
- 默认目录：`/tmp/ai_conversations/`
- 可通过 Django 设置 `AI_CONVERSATION_LOG_DIR` 自定义
- 文件命名格式：`conversation_YYYYMMDD_HHMMSS_mmm.txt`

### 3. 日志内容
每个日志文件包含：
- 会话开始信息
- 系统提示词
- 用户查询
- 所有 API 请求（完整的 payload）
- 所有 API 响应（完整的响应内容）
- 工具调用的参数和结果
- 模型的所有消息
- 最终结果

## 使用方法

### 基本使用
```python
from aiservice.agent import run_agent

# 正常调用，会自动记录日志
result = run_agent("查询最近24小时的负荷数据", debug=True)

# 返回结果中包含日志信息
if "debug" in result:
    print(f"会话ID: {result['debug']['session_id']}")
    print(f"日志文件: {result['debug']['log_file']}")
```

### 指定会话ID
```python
# 使用自定义会话ID
result = run_agent("查询数据", session_id="my_test_session")
```

### 查看日志文件
```python
from aiservice.agent import get_conversation_logs, read_conversation_log

# 获取所有日志文件列表
logs_info = get_conversation_logs()
print(f"共有 {len(logs_info['logs'])} 个日志文件")

# 读取特定会话的日志
log_content = read_conversation_log("20241201_143022_123")
print(log_content)
```

### 清理旧日志
```python
from aiservice.agent import cleanup_old_logs

# 清理7天前的日志
result = cleanup_old_logs(days=7)
print(result["message"])
```

## 日志文件格式

每个日志条目包含：
```
================================================================================
[2024-12-01 14:30:22.123] INFO - API_REQUEST
================================================================================
{
  "url": "https://api.deepseek.com/chat/completions",
  "timeout": 120,
  "headers": {...},
  "payload": {...},
  "payload_size": 1234
}
================================================================================
```

## 配置选项

在 Django 设置中添加：
```python
# 自定义日志目录
AI_CONVERSATION_LOG_DIR = "/path/to/your/logs"

# DeepSeek API 配置
DEEPSEEKKEY = "your-api-key"
DEEPSEEK_MODEL = "deepseek-chat"
DEEPSEEK_TIMEOUT = 120
DEEPSEEK_API_URL = "https://api.deepseek.com/chat/completions"
```

## 调试技巧

1. **对比不同会话**：使用相同的查询但不同的会话ID，对比日志文件找出差异
2. **分析API响应**：查看完整的API响应内容，了解模型的具体输出
3. **工具调用追踪**：查看工具调用的参数和结果，确保数据正确传递
4. **时间线分析**：按时间顺序查看整个对话流程

## 注意事项

1. 日志文件可能很大，建议定期清理
2. 日志包含敏感信息（API密钥等），注意文件权限
3. 生产环境建议关闭详细日志记录
4. 日志文件使用UTF-8编码，支持中文内容
