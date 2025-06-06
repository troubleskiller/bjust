# 在线推演完整功能说明

## 功能概述

在线推演功能现已支持完整的模型运行服务，用户可以：
1. 创建预测任务（支持典型场景和手动配置）
2. 实时查询任务状态
3. 获取任务结果（包含CSV字符串内容）
4. 停止正在运行的任务

## 核心特性

### ✅ 实际模型运行
- 支持调用真实的预测模型
- 后台异步执行，不阻塞用户界面
- 完整的进程管理和监控

### ✅ 任务状态管理
- `NOT_STARTED`: 任务已创建但未开始
- `IN_PROGRESS`: 任务正在运行中
- `COMPLETED`: 任务成功完成
- `ABORTED`: 任务被中止或失败

### ✅ 结果返回
- 任务完成后返回完整的CSV结果字符串
- 支持大文件结果的处理
- 包含任务执行时间等元信息

### ✅ 典型场景集成
- 支持使用典型场景UUID创建任务
- 返回典型场景的input.csv内容
- 包含场景元信息（名称、预测类型等）

## API接口

### 1. 创建预测任务
```http
POST /api/v1/online_deduction/tasks
```

**请求示例（典型场景）:**
```json
{
  "model_uuid": "uuid-model-001",
  "prediction_mode": "link",
  "scenario_type": "typical_scenario",
  "point_config": {
    "scenario_uuid": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
  },
  "param_config": {
    "frequency_band": "5.9GHz",
    "modulation_mode": "QPSK",
    "modulation_order": 4
  }
}
```

**响应示例:**
```json
{
  "message": "success",
  "code": "200",
  "data": {
    "task_uuid": "pred-task-12345",
    "prediction_mode": "link",
    "scenario_type": "typical_scenario",
    "status": "IN_PROGRESS",
    "message": "任务已启动",
    "scenario_csv_content": "39.9200,116.4200,30.0,39.9195,116.4195,1.5\n...",
    "scenario_info": {
      "scenario_name": "测试场景",
      "prediction_type": "单点预测",
      "tif_image_name": "nanjing"
    }
  }
}
```

### 2. 查询任务状态
```http
GET /api/v1/online_deduction/tasks/{task_uuid}/status
```

**响应示例:**
```json
{
  "message": "success",
  "code": "200",
  "data": {
    "task_uuid": "pred-task-12345",
    "status": "IN_PROGRESS",
    "message": "任务正在运行中",
    "created_at": "2024-01-01T12:00:00",
    "start_time": "2024-01-01T12:00:05",
    "prediction_mode": "link",
    "scenario_type": "typical_scenario",
    "process_status": {
      "status": "running",
      "pid": 12345
    }
  }
}
```

### 3. 获取任务结果
```http
GET /api/v1/online_deduction/tasks/{task_uuid}/result
```

**响应示例（任务完成）:**
```json
{
  "message": "success",
  "code": "200",
  "data": {
    "task_uuid": "pred-task-12345",
    "status": "COMPLETED",
    "message": "任务完成",
    "result_csv_content": "lat,lon,height,path_loss\n39.9200,116.4200,30.0,95.5\n39.9250,116.4250,25.0,98.2\n...",
    "completed_at": "2024-01-01T12:05:30"
  }
}
```

### 4. 停止任务
```http
POST /api/v1/online_deduction/tasks/{task_uuid}/stop
```

## 使用流程

### 标准使用流程
1. **创建任务** → 获得 `task_uuid`
2. **轮询状态** → 检查任务是否完成
3. **获取结果** → 获得CSV字符串内容

### 代码示例
```python
import requests
import time

# 1. 创建任务
task_data = {
    "model_uuid": "uuid-model-001",
    "prediction_mode": "link",
    "scenario_type": "typical_scenario",
    "point_config": {"scenario_uuid": "your-scenario-uuid"},
    "param_config": {"frequency_band": "5.9GHz"}
}
response = requests.post("http://localhost:9001/api/v1/online_deduction/tasks", 
                        json=task_data)
task_uuid = response.json()['data']['task_uuid']

# 2. 轮询状态
while True:
    status_response = requests.get(f"http://localhost:9001/api/v1/online_deduction/tasks/{task_uuid}/status")
    status = status_response.json()['data']['status']
    
    if status == 'COMPLETED':
        # 3. 获取结果
        result_response = requests.get(f"http://localhost:9001/api/v1/online_deduction/tasks/{task_uuid}/result")
        csv_content = result_response.json()['data']['result_csv_content']
        print(f"任务完成，结果长度: {len(csv_content)} 字符")
        break
    elif status == 'ABORTED':
        print("任务失败")
        break
    else:
        time.sleep(5)  # 等待5秒后再次检查
```

## 测试工具

### 完整功能测试
```bash
python test_online_deduction_full.py
```

这个测试脚本会：
1. 自动获取可用的典型场景
2. 创建预测任务
3. 监控任务进度
4. 获取最终结果
5. 演示停止任务功能

### 输出示例
```
🧪 在线推演完整功能测试
============================================================
正在获取典型场景列表...
✅ 找到典型场景: 测试场景_工厂园区 (UUID: a1b2c3d4-...)

============================================================
🚀 创建在线推演预测任务
============================================================
使用典型场景创建任务
✅ 任务创建成功!
任务UUID: pred-task-12345
任务状态: IN_PROGRESS
状态描述: 任务已启动

📊 查询任务状态: pred-task-12345
✅ 任务状态: COMPLETED
状态描述: 任务完成

📄 获取任务结果: pred-task-12345
✅ 任务状态: COMPLETED
📊 输出CSV结果:
==================================================
 1: lat,lon,height,path_loss
 2: 39.9200,116.4200,30.0,95.5
 3: 39.9250,116.4250,25.0,98.2
...
==================================================
CSV内容总长度: 1024 字符

🎊 测试完成! 获得 1024 字符的CSV结果
```

## 配置要求

### 环境变量
```python
# config.py
TASK_OUTPUT_DIR = 'storage/tasks/output'  # 任务输出目录
STORAGE_FOLDER = 'storage'                # 存储基础目录
```

### 目录结构
```
storage/
├── tasks/
│   ├── csv/           # 输入CSV文件
│   └── output/        # 输出结果目录
│       └── {task_uuid}/
│           └── result.csv
├── model/             # 模型文件
│   └── {model_uuid}/
│       ├── main.py
│       └── model_python_env/
└── typical_scenarios/ # 典型场景
    └── {type}_{uuid}/
        ├── input.csv
        └── scenario_metadata.json
```

## 技术特点

1. **异步执行**: 使用进程管理器后台运行模型
2. **状态持久化**: 任务状态存储在内存中（可扩展到数据库）
3. **错误处理**: 完善的异常捕获和错误信息返回
4. **资源管理**: 自动清理临时文件和进程资源
5. **扩展性**: 支持不同类型的预测模式和参数配置

## 注意事项

1. **模型路径**: 需要确保模型文件存在于指定路径
2. **环境配置**: Python环境和依赖需要正确配置
3. **权限问题**: 确保有足够的文件读写权限
4. **资源限制**: 进程管理器会限制同时运行的任务数量
5. **超时设置**: 长时间运行的任务需要适当的超时配置

## 扩展建议

1. **数据库存储**: 将任务状态持久化到数据库
2. **队列管理**: 实现任务队列和优先级管理
3. **结果缓存**: 缓存任务结果以提高访问速度
4. **通知机制**: 任务完成时的主动通知功能
5. **资源监控**: 添加CPU、内存使用情况监控 