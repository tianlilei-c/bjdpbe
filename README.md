# DPB2 - 传感器数据管理后端

基于Django和MongoDB构建的传感器数据管理后端系统，用于存储和管理工业设备传感器数据。

## 技术栈

- Python 3.8+
- Django 3.2+
- MongoDB
- MongoDB引擎（mongoengine）
- Django REST Framework

## 特性

- 基于MongoDB的高效数据存储
- 完整的REST API接口
- 支持按时间范围和字段值筛选数据
- 自动数据采集和模拟（每10秒）
- 支持批量数据操作
- 自动数据清理（保留3年数据）

## 安装与设置

### 环境需求

- Python 3.8+
- MongoDB 服务器（本地或远程）

### 安装步骤

1. 克隆项目代码
2. 安装依赖：
   ```
   pip install -r requirements.txt
   ```
3. 运行开发服务器：
   ```
   python manage.py runserver
   ```

## API文档

### 数据查询

- **GET /api/sensor-data/** - 获取传感器数据列表（支持分页）
  - 参数：
    - `start_time`: 开始时间（格式：YYYY-MM-DD HH:MM:SS）
    - `end_time`: 结束时间（格式：YYYY-MM-DD HH:MM:SS）
    - `field`: 字段名称
    - `value`: 字段值
    - `value_gt`: 大于指定值
    - `value_lt`: 小于指定值
    - `page`: 页码
    - `page_size`: 每页数据量

- **GET /api/sensor-data/{id}/** - 获取单条传感器数据

- **GET /api/sensor-data/latest/** - 获取最新一条传感器数据

### 数据创建

- **POST /api/sensor-data/** - 创建新的传感器数据（支持单条或批量）

### 数据更新

- **PUT /api/sensor-data/{id}/** - 更新传感器数据

### 数据删除

- **DELETE /api/sensor-data/{id}/** - 删除单条传感器数据
- **DELETE /api/sensor-data/batch_delete/** - 批量删除传感器数据
  - 参数：
    - `start_time`: 开始时间（格式：YYYY-MM-DD HH:MM:SS）
    - `end_time`: 结束时间（格式：YYYY-MM-DD HH:MM:SS）

## 数据采集

项目包含一个Django管理命令，用于模拟数据采集：

```
# 单次采集
python manage.py fetch_data

# 连续采集（每10秒）
python manage.py fetch_data --continuous
```

在实际生产环境中，可以将该命令配置为定时任务，例如：

```
# 使用crontab（Linux/Mac）
*/10 * * * * cd /path/to/project && python manage.py fetch_data

# 使用Windows任务计划程序
# 创建一个每10秒运行一次的任务，调用以下命令：
python C:\path\to\project\manage.py fetch_data
```

## 数据维护

数据将自动保留3年，超过3年的数据会自动删除。这是通过MongoDB的TTL索引实现的。 