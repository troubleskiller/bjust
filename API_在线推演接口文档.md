# 在线推演API接口文档

> **版本**: v1.0  
> **基础URL**: `http://localhost:9001/api/v1`  
> **更新时间**: 2024-01-XX

## 目录

1. [典型场景管理](#典型场景管理)
2. [在线推演任务管理](#在线推演任务管理)
3. [错误码说明](#错误码说明)
4. [数据类型定义](#数据类型定义)

---

## 典型场景管理

### 1. 获取典型场景列表

获取所有可用的典型场景列表，用于场景选择。

**接口地址**: `GET /typical_scenarios`

**请求参数**: 无

**响应格式**:
```json
{
  "code": "200",
  "message": "success",
  "data": {
    "scenarios": [
      {
        "uuid": "single_point_0ee6eb04-ded7-4fe3-a1d7-f06139e92536",
        "name": "测试场景_工厂园区",
        "type": "directory_with_metadata",
        "prediction_type": "单点预测",
        "prediction_type_code": "single_point",
        "tif_image_name": "nanjing",
        "created_at": "2025-06-06T10:44:42.547922",
        "description": "典型场景: 测试场景_工厂园区 (单点预测)"
      }
    ]
  }
}
```

**前端示例代码**:
```javascript
// 获取典型场景列表
async function getTypicalScenarios() {
  try {
    const response = await fetch('/api/v1/typical_scenarios');
    const result = await response.json();
    
    if (result.code === '200') {
      return result.data.scenarios;
    } else {
      throw new Error(result.message);
    }
  } catch (error) {
    console.error('获取典型场景失败:', error);
    throw error;
  }
}
```

---

## 在线推演任务管理

### 1. 创建预测任务

创建新的在线推演预测任务，支持三种场景类型。

**接口地址**: `POST /online_deduction/tasks`

**请求头**:
```
Content-Type: application/json
```

**请求参数**:
```json
{
  "model_uuid": "MODEL-663477c0242d4fc89bbfa0fc43e96527",
  "prediction_mode": "link",
  "scenario_type": "typical_scenario",
  "point_config": {
    "scenario_uuid": "single_point_0ee6eb04-ded7-4fe3-a1d7-f06139e92536"
  },
  "param_config": {
    "frequency_band": "5.9GHz",
    "modulation_mode": "QPSK",
    "modulation_order": 4
  }
}
```

**参数说明**:

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| model_uuid | string | 是 | 模型UUID |
| prediction_mode | string | 是 | 预测模式: `point`/`link`/`situation`/`small_scale` |
| scenario_type | string | 是 | 场景类型: `manual_selection`/`typical_scenario`/`custom_upload` |
| point_config | object | 是 | 点位配置（根据scenario_type变化） |
| param_config | object | 是 | 参数配置 |

**场景类型配置**:

#### 典型场景 (typical_scenario)
```json
{
  "scenario_type": "typical_scenario",
  "point_config": {
    "scenario_uuid": "single_point_0ee6eb04-ded7-4fe3-a1d7-f06139e92536"
  }
}
```

#### 自主选点 (manual_selection)
```json
{
  "scenario_type": "manual_selection",
  "point_config": {
    "scenario_description": "城市商业区信号覆盖预测",
    "tx_pos_list": [
      {"lat": 39.9200, "lon": 116.4200, "height": 30.0}
    ],
    "rx_pos_list": [
      {"lat": 39.9195, "lon": 116.4195, "height": 1.5},
      {"lat": 39.9205, "lon": 116.4205, "height": 1.5}
    ]
  }
}
```

#### 自定义上传 (custom_upload)
```json
{
  "scenario_type": "custom_upload",
  "point_config": {
    "scenario_description": "用户自定义场景",
    "tx_pos_list": [...],
    "rx_pos_list": [...]
  }
}
```

**响应格式**:
```json
{
  "code": "200",
  "message": "success", 
  "data": {
    "task_uuid": "12345678-1234-1234-1234-123456789abc",
    "task_folder_name": "ONLINE-DEDUCTION-12345678-1234-1234-1234-123456789abc",
    "task_folder_path": "/storage/tasks/ONLINE-DEDUCTION-12345678-1234-1234-1234-123456789abc",
    "prediction_mode": "link",
    "scenario_type": "typical_scenario",
    "status": "IN_PROGRESS",
    "message": "任务已启动",
    "scenario_csv_content": "39.9200,116.4200,30.0,39.9195,116.4195,1.5,5900\n...",
    "scenario_info": {
      "scenario_name": "测试场景_工厂园区",
      "prediction_type": "单点预测",
      "tif_image_name": "nanjing",
      "created_at": "2025-06-06T10:44:42.547922"
    }
  }
}
```

**前端示例代码**:
```javascript
// 创建典型场景任务
async function createTypicalScenarioTask(scenarioUuid, modelUuid) {
  const requestData = {
    model_uuid: modelUuid,
    prediction_mode: "link",
    scenario_type: "typical_scenario",
    point_config: {
      scenario_uuid: scenarioUuid
    },
    param_config: {
      frequency_band: "5.9GHz",
      modulation_mode: "QPSK",
      modulation_order: 4
    }
  };

  try {
    const response = await fetch('/api/v1/online_deduction/tasks', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(requestData)
    });

    const result = await response.json();
    
    if (result.code === '200') {
      return result.data;
    } else {
      throw new Error(result.message);
    }
  } catch (error) {
    console.error('创建任务失败:', error);
    throw error;
  }
}

// 创建自主选点任务
async function createManualSelectionTask(txPositions, rxPositions, modelUuid) {
  const requestData = {
    model_uuid: modelUuid,
    prediction_mode: "link",
    scenario_type: "manual_selection",
    point_config: {
      scenario_description: "用户自主选点预测",
      tx_pos_list: txPositions,
      rx_pos_list: rxPositions
    },
    param_config: {
      frequency_band: "5.9GHz",
      modulation_mode: "QPSK",
      modulation_order: 4
    }
  };

  // 发送请求逻辑同上...
}
```

### 2. 查询任务状态

查询指定任务的运行状态和进度。

**接口地址**: `GET /online_deduction/tasks/{task_uuid}/status`

**路径参数**:
- `task_uuid`: 任务UUID

**响应格式**:
```json
{
  "code": "200",
  "message": "success",
  "data": {
    "task_uuid": "12345678-1234-1234-1234-123456789abc",
    "status": "IN_PROGRESS",
    "message": "任务正在进行中",
    "created_at": "2024-01-15T10:30:00.000Z",
    "start_time": "2024-01-15T10:30:01.000Z",
    "end_time": null,
    "prediction_mode": "link",
    "scenario_type": "typical_scenario",
    "task_folder_path": "/storage/tasks/ONLINE-DEDUCTION-12345678-1234-1234-1234-123456789abc",
    "process_status": {
      "status": "running",
      "pid": 12345
    }
  }
}
```

**状态说明**:
- `NOT_STARTED`: 任务未开始
- `IN_PROGRESS`: 任务进行中
- `COMPLETED`: 任务已完成
- `ABORTED`: 任务已中止

**前端示例代码**:
```javascript
// 查询任务状态
async function getTaskStatus(taskUuid) {
  try {
    const response = await fetch(`/api/v1/online_deduction/tasks/${taskUuid}/status`);
    const result = await response.json();
    
    if (result.code === '200') {
      return result.data;
    } else {
      throw new Error(result.message);
    }
  } catch (error) {
    console.error('查询任务状态失败:', error);
    throw error;
  }
}

// 轮询任务状态
async function pollTaskStatus(taskUuid, callback, interval = 3000) {
  const poll = async () => {
    try {
      const status = await getTaskStatus(taskUuid);
      callback(status);
      
      if (status.status === 'COMPLETED' || status.status === 'ABORTED') {
        return; // 任务结束，停止轮询
      }
      
      setTimeout(poll, interval);
    } catch (error) {
      console.error('轮询状态失败:', error);
    }
  };
  
  poll();
}
```

### 3. 获取任务结果

获取已完成任务的预测结果数据。

**接口地址**: `GET /online_deduction/tasks/{task_uuid}/result`

**路径参数**:
- `task_uuid`: 任务UUID

**响应格式**:
```json
{
  "code": "200",
  "message": "success",
  "data": {
    "task_uuid": "12345678-1234-1234-1234-123456789abc",
    "status": "COMPLETED",
    "message": "任务完成",
    "result_csv_content": "距离,路径损耗\n100.0,95.5\n200.0,98.2\n300.0,101.1\n...",
    "completed_at": "2024-01-15T10:35:00.000Z",
    "started_at": "2024-01-15T10:30:01.000Z"
  }
}
```

**CSV格式说明**:
- 第一列: 距离（米）
- 第二列: 路径损耗（dB）

**前端示例代码**:
```javascript
// 获取任务结果
async function getTaskResult(taskUuid) {
  try {
    const response = await fetch(`/api/v1/online_deduction/tasks/${taskUuid}/result`);
    const result = await response.json();
    
    if (result.code === '200') {
      return result.data;
    } else {
      throw new Error(result.message);
    }
  } catch (error) {
    console.error('获取任务结果失败:', error);
    throw error;
  }
}

// 解析CSV内容
function parseCSVResult(csvContent) {
  const lines = csvContent.trim().split('\n');
  const data = [];
  
  for (let i = 0; i < lines.length; i++) {
    const [distance, pathLoss] = lines[i].split(',');
    data.push({
      distance: parseFloat(distance),
      pathLoss: parseFloat(pathLoss)
    });
  }
  
  return data;
}
```

### 4. 停止运行任务

停止正在运行的任务。

**接口地址**: `POST /online_deduction/tasks/{task_uuid}/stop`

**路径参数**:
- `task_uuid`: 任务UUID

**响应格式**:
```json
{
  "code": "200",
  "message": "success",
  "data": {
    "task_uuid": "12345678-1234-1234-1234-123456789abc",
    "status": "ABORTED",
    "message": "任务已被手动停止"
  }
}
```

**前端示例代码**:
```javascript
// 停止任务
async function stopTask(taskUuid) {
  try {
    const response = await fetch(`/api/v1/online_deduction/tasks/${taskUuid}/stop`, {
      method: 'POST'
    });
    
    const result = await response.json();
    
    if (result.code === '200') {
      return result.data;
    } else {
      throw new Error(result.message);
    }
  } catch (error) {
    console.error('停止任务失败:', error);
    throw error;
  }
}
```

---

## 错误码说明

| 错误码 | 说明 | 常见原因 |
|--------|------|----------|
| 200 | 请求成功 | - |
| 400 | 请求参数错误 | 缺少必填字段、参数格式不正确 |
| 404 | 资源不存在 | 任务UUID不存在、典型场景不存在 |
| 500 | 服务器内部错误 | 服务器异常、数据库连接失败 |

**错误响应格式**:
```json
{
  "code": "400",
  "message": "Missing required field: model_uuid",
  "data": null
}
```

---

## 数据类型定义

### TaskStatus (任务状态)
```typescript
type TaskStatus = "NOT_STARTED" | "IN_PROGRESS" | "COMPLETED" | "ABORTED";
```

### PredictionMode (预测模式)
```typescript
type PredictionMode = "point" | "link" | "situation" | "small_scale";
```

### ScenarioType (场景类型)
```typescript
type ScenarioType = "manual_selection" | "typical_scenario" | "custom_upload";
```

### Position (位置信息)
```typescript
interface Position {
  lat: number;    // 纬度
  lon: number;    // 经度  
  height: number; // 高度（米）
}
```

### TypicalScenario (典型场景)
```typescript
interface TypicalScenario {
  uuid: string;
  name: string;
  type: string;
  prediction_type: string;
  prediction_type_code: string;
  tif_image_name: string;
  created_at: string;
  description: string;
}
```

### Task (任务信息)
```typescript
interface Task {
  task_uuid: string;
  task_folder_name: string;
  task_folder_path: string;
  prediction_mode: PredictionMode;
  scenario_type: ScenarioType;
  status: TaskStatus;
  message: string;
  created_at: string;
  start_time?: string;
  end_time?: string;
  result_csv_content?: string;
  scenario_csv_content?: string;
  scenario_info?: object;
}
```

---

## 完整使用示例

```javascript
// 完整的在线推演流程示例
class OnlineDeductionClient {
  constructor(baseUrl = '/api/v1') {
    this.baseUrl = baseUrl;
  }

  // 获取典型场景列表
  async getScenarios() {
    const response = await fetch(`${this.baseUrl}/typical_scenarios`);
    const result = await response.json();
    return result.data.scenarios;
  }

  // 创建任务
  async createTask(config) {
    const response = await fetch(`${this.baseUrl}/online_deduction/tasks`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(config)
    });
    const result = await response.json();
    
    if (result.code !== '200') {
      throw new Error(result.message);
    }
    
    return result.data;
  }

  // 监控任务直到完成
  async monitorTask(taskUuid, onProgress) {
    return new Promise((resolve, reject) => {
      const checkStatus = async () => {
        try {
          const response = await fetch(`${this.baseUrl}/online_deduction/tasks/${taskUuid}/status`);
          const result = await response.json();
          
          if (result.code !== '200') {
            reject(new Error(result.message));
            return;
          }
          
          const status = result.data;
          onProgress(status);
          
          if (status.status === 'COMPLETED') {
            // 获取结果
            const resultResponse = await fetch(`${this.baseUrl}/online_deduction/tasks/${taskUuid}/result`);
            const resultData = await resultResponse.json();
            resolve(resultData.data);
          } else if (status.status === 'ABORTED') {
            reject(new Error('Task was aborted'));
          } else {
            // 继续监控
            setTimeout(checkStatus, 3000);
          }
        } catch (error) {
          reject(error);
        }
      };
      
      checkStatus();
    });
  }

  // 使用示例
  async runPrediction() {
    try {
      // 1. 获取典型场景
      const scenarios = await this.getScenarios();
      const selectedScenario = scenarios[0];
      
      // 2. 创建任务
      const task = await this.createTask({
        model_uuid: "MODEL-663477c0242d4fc89bbfa0fc43e96527",
        prediction_mode: "link",
        scenario_type: "typical_scenario",
        point_config: {
          scenario_uuid: selectedScenario.uuid
        },
        param_config: {
          frequency_band: "5.9GHz",
          modulation_mode: "QPSK",
          modulation_order: 4
        }
      });
      
      console.log('任务创建成功:', task.task_uuid);
      
      // 3. 监控任务进度
      const result = await this.monitorTask(task.task_uuid, (status) => {
        console.log('任务状态:', status.status, status.message);
      });
      
      console.log('任务完成，结果:', result.result_csv_content);
      
    } catch (error) {
      console.error('预测失败:', error);
    }
  }
}

// 使用
const client = new OnlineDeductionClient();
client.runPrediction();
```

---

**联系方式**: 如有API接口问题，请联系后端开发团队。 