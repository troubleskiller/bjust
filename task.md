# 技术文档

本文档详细描述了项目的后端API接口，包括各个模块的功能、请求参数、响应数据结构等。

## **目录**

1.  [首页 (Homepage)](#首页-homepage)
2.  [在线推演 - 通用接口 (Online Deduction - Common APIs)](#在线推演---通用接口-online-deduction---common-apis)
3.  [在线推演 - 单点预测 (Online Deduction - Single Point Prediction)](#在线推演---单点预测-online-deduction---single-point-prediction)
4.  [在线推演 - 态势预测 (Online Deduction - Situation Prediction)](#在线推演---态势预测-online-deduction---situation-prediction)
5.  [在线推演 - 小尺度预测 (Online Deduction - Small Scale Prediction)](#在线推演---小尺度预测-online-deduction---small-scale-prediction)
6.  [模型广场 (Model Plaza)](#模型广场-model-plaza)
7.  [模型详情介绍 (Model Detail Introduction)](#模型详情介绍-model-detail-introduction)
8.  [信道数据 (Channel Data Management)](#信道数据-channel-data-management)
9.  [模型验证 (Model Validation / PK)](#模型验证-model-validation--pk)

---

## **首页 (Homepage)**

### **获取最佳实践案例 (Get Best Practice Cases)**
**接口名称**: `getBestPracticalCase()`
**请求方法**: `GET`
**路径**: `/api/v1/homepage/best_cases`

**描述**: 获取最佳实践案例列表，用于首页展示。后端从预设的文件夹中读取案例信息。

**请求参数**: 无

**响应结构**:
```json
{
  "message": "success",
  "code": "200",
  "data": [
    {
      "case_dir_name": "case_folder_highway_scenario",
      "case_img": "/storage/best_cases/case_folder_highway_scenario/thumbnail.jpg",
      "case_type": "real_data",
      "case_title": "高速公路场景信道特性分析",
      "model_name": "Plana3.0,RayTracerX",
      "model_type_name": "态势感知模型,大尺度模型",
      "create_date": "2023-05-15"
    }
    // ... more cases
  ]
}
```

**字段说明**:
| 字段名            | 类型   | 示例                                          | 备注                                                         |
| ----------------- | ------ | --------------------------------------------- | ------------------------------------------------------------ |
| `case_dir_name`   | string | "case_folder_highway_scenario"                | 案例文件夹名称 (用于后续加载案例详情或跳转)                  |
| `case_img`        | string | "/storage/best_cases/uuid_xxxx/thumbnail.jpg" | 案例展示图片路径                                             |
| `case_type`       | string | "real_data"                                   | 案例类型: "real_data" (实测案例), "simulation" (仿真案例), "no_label" (无标签) |
| `case_title`      | string | "高速公路场景信道特性分析"                    | 案例标题                                                     |
| `model_name`      | string | "Plana3.0,RayTracerX"                         | 案例中使用的模型名称，可能多个，逗号分隔                     |
| `model_type_name` | string | "态势感知模型,大尺度模型"                     | 对应模型类型名称，逗号分隔                                   |
| `create_date`     | string | "2023-05-15"                                  | 案例创建或指定日期                                           |

---

## **在线推演 - 通用接口 (Online Deduction - Common APIs)**

### **获取模型列表 (Get Model List by Task Type)**
**接口名称**: `getOnlineModelsByTaskType()`
**请求方法**: `GET`
**路径**: `/api/v1/online_deduction/models`

**描述**: 根据任务类型获取可用的在线推演模型列表。

**请求参数**:
| 参数名      | 类型   | 示例                                | 备注                                                                                                                                 |
|-------------|--------|-------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------|
| `task_type` | string | "single_point_prediction"         | 任务类型: "single_point_prediction" (单点预测), "situation_prediction" (态势预测), "small_scale_prediction" (小尺度预测) |

**响应结构**:
```json
{
  "message": "success",
  "code": "200",
  "data": [
    {
      "model_uuid": "uuid-model-001",
      "model_name": "RayTracer-Pro",
      "model_description": "基于射线追踪的精确信道模型。",
      "model_img": "/storage/models/raytracer_pro_thumb.jpg",
      "model_doc_url": "/models/uuid-model-001/documentation"
    }
    // ... more models
  ]
}
```

**字段说明**:
| 字段名              | 类型       | 示例                                       | 备注                     |
|---------------------|------------|--------------------------------------------|--------------------------|
| `model_uuid`        | string     | "uuid-model-001"                           | 模型唯一标识             |
| `model_name`        | string     | "RayTracer-Pro"                            | 模型名称                 |
| `model_description` | string     | "基于射线追踪的精确信道模型。"                | 模型简短描述             |
| `model_img`         | string     | "/storage/models/raytracer_pro_thumb.jpg"  | 模型缩略图路径           |
| `model_doc_url`     | string     | "/models/uuid-model-001/documentation"     | 模型详细文档页面链接     |

### **创建预测任务 (Create Prediction Task) - 统一接口**
**接口名称**: `createPredictionTask()`
**请求方法**: `POST`
**路径**: `/api/v1/online_deduction/tasks`

**描述**: 创建预测任务的统一接口，通过prediction_mode区分不同类型的预测任务（单点预测、链路预测、态势预测、小尺度预测），返回任务ID。

**请求体**:
```json
{
  "model_uuid": "uuid-model-001",
  "prediction_mode": "link",
  "point_config": {
    "tx_pos_list": [
      { "lat": 39.915, "lon": 116.404, "height": 30.0 }
    ],
    "rx_pos_list": [
      { "lat": 39.916, "lon": 116.405, "height": 1.5 },
      { "lat": 39.917, "lon": 116.406, "height": 1.5 },
      { "lat": 39.918, "lon": 116.407, "height": 1.5 }
    ],
    "area_bounds": {
      "min_lat": 39.900, "min_lon": 116.390,
      "max_lat": 39.930, "max_lon": 116.420
    },
    "resolution_m": 10
  },
  "param_config": {
    "frequency_band": "5.9GHz",
    "modulation_mode": "QPSK",
    "modulation_order": 4
  }
}
```

**字段说明**:
| 字段名              | 类型       | 示例                          | 备注                                  |
|---------------------|------------|-------------------------------|---------------------------------------|
| `model_uuid`        | string     | "uuid-model-001"              | 所选模型唯一标识                      |
| `prediction_mode`   | string     | "point" / "link" / "situation" / "small_scale" | 预测模式：<br/>- "point": 单点预测<br/>- "link": 链路预测<br/>- "situation": 态势预测<br/>- "small_scale": 小尺度预测 |
| `point_config`      | object     | 见下                             | 点位配置                              |
| `param_config`      | object     | 见下                             | 参数配置                              |

#### **`point_config` 字段说明**:
| 字段名          | 类型   | 示例                                                                 | 备注                                    |
|-----------------|--------|----------------------------------------------------------------------|-----------------------------------------|
| `tx_pos_list`   | array  | `[{ "lat": 39.915, "lon": 116.404, "height": 30.0 }, ...]`          | 发射机位置列表 (纬度, 经度, 海拔高度米) |
| `rx_pos_list`   | array  | `[{ "lat": ..., "lon": ..., "height": ... }, ...]`                  | 接收机点列表 (用于 prediction_mode="point" 和 "link") |
| `area_bounds`   | object | `{ "min_lat": ..., "min_lon": ..., "max_lat": ..., "max_lon": ... }` | (可选) 预测区域边界 (用于 prediction_mode="situation") |
| `resolution_m`  | float  | 10                                                                   | (可选) 热力图空间分辨率 (米) (用于 prediction_mode="situation") |

**使用说明**:
- **prediction_mode="point"**: 单点预测模式，使用 `tx_pos_list` 和 `rx_pos_list` 定义离散的发射-接收点对
- **prediction_mode="link"**: 链路预测模式，使用 `tx_pos_list` 和 `rx_pos_list` 定义发射机和接收路径点序列  
- **prediction_mode="situation"**: 态势预测模式，使用 `tx_pos_list` 定义发射机，可选 `area_bounds` 和 `resolution_m` 定义预测区域
- **prediction_mode="small_scale"**: 小尺度预测模式，使用 `tx_pos_list` 和 `rx_pos_list`，需要额外的调制参数

#### **`param_config` 字段说明**:
| 字段名           | 类型   | 示例       | 备注         |
|------------------|--------|------------|--------------|
| `frequency_band` | string | "5.9GHz"   | 频段 (e.g., "2.4GHz", "5.9GHz", "28GHz") |
| `modulation_mode`| string | "QPSK"     | (可选) 调制方式，用于 prediction_mode="small_scale" (e.g., "BPSK", "QPSK", "16QAM", "64QAM") |
| `modulation_order`| int   | 4          | (可选) 调制阶数，用于 prediction_mode="small_scale" (e.g., 2, 4, 16, 64) |

**响应结构**:
```json
{
  "message": "success",
  "code": "200",
  "data": {
    "task_uuid": "pred-task-uuid-001",
    "prediction_mode": "link"
  }
}
```

---

## **在线推演 - 单点预测 (Online Deduction - Single Point Prediction)**
*(包含单点模式和链路模式)*

### **获取单点预测任务结果 (Get Single Point Prediction Task Result)**
**接口名称**: `getSinglePointPredictionTaskResult()`
**请求方法**: `GET`
**路径**: `/api/v1/online_deduction/tasks/{task_uuid}/results`

**描述**: 增量获取单点预测任务的结果。结果格式适应单点或链路模式。

**请求参数 (路径)**:
| 参数名        | 类型   | 示例                | 备注                   |
|---------------|--------|---------------------|------------------------|
| `task_uuid`   | string | "pred-task-uuid-001" | 任务唯一标识 (路径参数) |

**请求参数 (Query)**:
| 参数名        | 类型   | 示例                | 备注                                      |
|---------------|--------|---------------------|-------------------------------------------|
| `next_index`  | int    | 0                   | (可选) 下一个要获取的点的序号 (从0开始)   |
| `batch_size`  | int    | 10                  | (可选) 期望获取点的数量，默认返回所有新结果 |


**响应结构 (prediction_mode = "point")**:
```json
{
  "message": "success",
  "code": "200",
  "data": {
    "task_uuid": "pred-task-uuid-001",
    "status": "IN_PROGRESS",
    "prediction_mode": "point",
    "total_points": 5,
    "completed_points": 2,
    "results": [
      {
        "rx_index": 0,
        "pos": { "lat": 39.916, "lon": 116.405, "height": 1.5 },
        "path_loss_db": 95.5
      },
      {
        "rx_index": 1,
        "pos": { "lat": 39.917, "lon": 116.406, "height": 1.5 },
        "path_loss_db": 98.2
      }
    ]
  }
}
```

**响应结构 (prediction_mode = "link")**:
```json
{
  "message": "success",
  "code": "200",
  "data": {
    "task_uuid": "pred-task-uuid-001",
    "status": "COMPLETED",
    "prediction_mode": "link",
    "total_samples": 100,
    "completed_samples": 100,
    "results": [
      {
        "sample_index": 0,
        "pos": { "lat": 39.916, "lon": 116.405, "height": 1.5 },
        "distance_from_start_m": 0.0,
        "path_loss_db": 95.5
      },
      {
        "sample_index": 99,
        "pos": { "lat": 39.920, "lon": 116.410, "height": 1.5 },
        "distance_from_start_m": 550.0,
        "path_loss_db": 102.1
      }
    ],
    "overall_rmse_db": 5.2
  }
}
```

**通用结果字段说明**:
| 字段名                 | 类型   | 示例                  | 备注                                      |
|------------------------|--------|-----------------------|-------------------------------------------|
| `task_uuid`            | string | "pred-task-uuid-001"   | 任务唯一标识                              |
| `status`               | string | "IN_PROGRESS"         | 任务状态 ("PENDING", "IN_PROGRESS", "COMPLETED", "FAILED") |
| `prediction_mode`      | string | "point" / "link"      | 预测模式                                  |
| `total_points`         | int    | 5                     | (point mode) 总Rx点数                     |
| `completed_points`     | int    | 2                     | (point mode) 已完成计算的点数             |
| `total_samples`        | int    | 100                   | (link mode) 链路上总采样点数            |
| `completed_samples`    | int    | 100                   | (link mode) 已完成计算的采样点数        |
| `results`              | array  | 见特定模式             | 结果列表                                  |
| `overall_rmse_db`      | float  | 5.2                   | (link mode, 可选) 如果有实测数据对比时提供 |

**`results` 元素字段说明 (point mode)**:
| 字段名         | 类型   | 示例                                                 | 备注                     |
|----------------|--------|------------------------------------------------------|--------------------------|
| `rx_index`     | int    | 0                                                    | 接收机在请求列表中的索引 |
| `pos`          | object | `{ "lat": 39.916, "lon": 116.405, "height": 1.5 }`   | 接收机点位坐标           |
| `path_loss_db` | float  | 95.5                                                 | 预测的路径损耗 (dB)      |

**`results` 元素字段说明 (link mode)**:
| 字段名                  | 类型   | 示例                                                 | 备注                     |
|-------------------------|--------|------------------------------------------------------|--------------------------|
| `sample_index`          | int    | 0                                                    | 路径上的采样点索引       |
| `pos`                   | object | `{ "lat": 39.916, "lon": 116.405, "height": 1.5 }`   | 采样点坐标               |
| `distance_from_start_m` | float  | 0.0                                                  | 距路径起点的距离 (米)    |
| `path_loss_db`          | float  | 95.5                                                 | 预测的路径损耗 (dB)      |

---

## **在线推演 - 态势预测 (Online Deduction - Situation Prediction)**

### **获取态势预测任务结果 (Get Situation Prediction Task Result)**
**接口名称**: `getSituationPredictionTaskResult()`
**请求方法**: `GET`
**路径**: `/api/v1/online_deduction/tasks/{task_uuid}/result`

**描述**: 获取态势预测任务的结果（热力图数据）。通常一次性返回。

**请求参数 (路径)**:
| 参数名      | 类型   | 示例                | 备注                   |
|-------------|--------|---------------------|------------------------|
| `task_uuid` | string | "pred-task-uuid-001" | 任务唯一标识 (路径参数) |

**响应结构**:
```json
{
  "message": "success",
  "code": "200",
  "data": {
    "task_uuid": "pred-task-uuid-001",
    "status": "COMPLETED",
    "prediction_mode": "situation",
    "result": {
      "heatmap_data_type": "grid",
      "grid_origin": { "lat": 39.900, "lon": 116.390 },
      "cell_size_deg": { "lat_delta": 0.0001, "lon_delta": 0.0001 },
      "rows": 300,
      "cols": 300,
      "values": [
        [100.5, 101.2, ...],
        [102.1, 103.0, ...],
      ],
      "value_unit": "dB"
    }
    // Alternative for large data:
    // "result_url": "/storage/tasks/pred-task-uuid-001/heatmap.json"
  }
}
```
**字段说明**:
| 字段名                | 类型   | 示例                                      | 备注                                                                 |
|-----------------------|--------|-------------------------------------------|----------------------------------------------------------------------|
| `task_uuid`           | string | "pred-task-uuid-001"                       | 任务唯一标识                                                         |
| `status`              | string | "COMPLETED"                               | 任务状态 ("PENDING", "IN_PROGRESS", "COMPLETED", "FAILED")             |
| `prediction_mode`     | string | "situation"                               | 预测模式                                                             |
| `result.heatmap_data_type`| string | "grid"                                    | 热力图数据格式 (e.g., "grid" for direct array, "geojson_url" for a file link) |
| `result.grid_origin`  | object | `{ "lat": ..., "lon": ... }`              | (if type="grid") 网格左下角原点                                      |
| `result.cell_size_deg`| object | `{ "lat_delta": ..., "lon_delta": ... }`  | (if type="grid") 网格单元大小 (度) 或 `cell_size_m` (米)             |
| `result.rows`         | int    | 300                                       | (if type="grid") 网格行数                                            |
| `result.cols`         | int    | 300                                       | (if type="grid") 网格列数                                            |
| `result.values`       | array  | `[[100.5, ...], ...]`                     | (if type="grid") 二维数组的路径损耗值 (行优先或列优先)               |
| `result.value_unit`   | string | "dB"                                      | 热力图值的单位                                                       |
| `result_url`          | string | (可选)                                     | 如果数据量大，可能提供一个下载链接                                   |

---

## **在线推演 - 小尺度预测 (Online Deduction - Small Scale Prediction)**

### **获取小尺度预测任务结果 (Get Small Scale Prediction Task Result)**
**接口名称**: `getSmallScalePredictionTaskResult()`
**请求方法**: `GET`
**路径**: `/api/v1/online_deduction/tasks/{task_uuid}/result`

**描述**: 获取小尺度预测任务的结果，包括PDP和BER/SNR数据。通常一次性返回。

**请求参数 (路径)**:
| 参数名      | 类型   | 示例                | 备注                   |
|-------------|--------|---------------------|------------------------|
| `task_uuid` | string | "pred-task-uuid-001" | 任务唯一标识 (路径参数) |

**响应结构**:
```json
{
  "message": "success",
  "code": "200",
  "data": {
    "task_uuid": "pred-task-uuid-001",
    "status": "COMPLETED",
    "prediction_mode": "small_scale",
    "results": {
      "pdp_data": {
        "time_delays_ns": [0, 10, 20, 30, ...],
        "power_levels_dbm": [
          { "pos": {"lat": 39.916, "lon": 116.405, "height": 1.5}, "pdp": [-80, -85, -90, -100, ...] },
          { "pos": {"lat": 39.917, "lon": 116.406, "height": 1.5}, "pdp": [-82, -83, -92, -105, ...] }
        ]
        // "pdp_data_url": "/storage/tasks/pred-task-uuid-001/pdp_data.json"
      },
      "ber_snr_data": {
        "snr_values_db": [0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20],
        "ber_values": [
          { "pos": {"lat": 39.916, "lon": 116.405, "height": 1.5}, "ber": [0.5, 0.3, 0.1, 0.01, ...] },
          { "pos": {"lat": 39.917, "lon": 116.406, "height": 1.5}, "ber": [0.45, 0.28, 0.08, 0.008, ...] }
        ]
        // "ber_snr_data_url": "/storage/tasks/pred-task-uuid-001/ber_snr_data.json"
      }
    }
  }
}
```
**字段说明**:
| 字段名                    | 类型   | 示例                                      | 备注                                                                 |
|---------------------------|--------|-------------------------------------------|----------------------------------------------------------------------|
| `task_uuid`               | string | "pred-task-uuid-001"                       | 任务唯一标识                                                         |
| `status`                  | string | "COMPLETED"                               | 任务状态 ("PENDING", "IN_PROGRESS", "COMPLETED", "FAILED")             |
| `prediction_mode`         | string | "small_scale"                             | 预测模式                                                             |
| `results.pdp_data`        | object |                                           | 功率延迟谱 (Power Delay Profile) 数据                                 |
| `results.pdp_data.time_delays_ns` | array | `[0, 10, 20, ...]`                    | 采样时间延迟 (纳秒)                                                  |
| `results.pdp_data.power_levels_dbm` | array | `[{pos:{...}, pdp:[-80,...]}, ...]` | 对应每个采样点的PDP数据 (pdp是功率值dBm数组)                       |
| `results.pdp_data.pdp_data_url` | string | (可选)                                 | PDP数据文件下载链接 (如果数据复杂)                                    |
| `results.ber_snr_data`    | object |                                           | BER vs SNR 数据                                                      |
| `results.ber_snr_data.snr_values_db` | array | `[0, 2, 4, ...]`                     | SNR值列表 (dB)                                                       |
| `results.ber_snr_data.ber_values` | array | `[{pos:{...}, ber:[0.5,...]}, ...]`    | 对应每个采样点的BER曲线 (ber是误码率数组)                            |
| `results.ber_snr_data.ber_snr_data_url` | string | (可选)                         | BER/SNR数据文件下载链接 (如果数据复杂)                               |

---

## **模型广场 (Model Plaza)**

### **获取模型列表 (Get Model List)**
**接口名称**: `getModels()`
**请求方法**: `GET`
**路径**: `/api/v1/models`

**描述**: 获取模型列表，支持筛选和分页。

**请求参数**:
| 参数名                  | 类型   | 示例                      | 备注                                                                      |
|-------------------------|--------|---------------------------|---------------------------------------------------------------------------|
| `page`                  | int    | 1                         | (可选) 页码，默认1                                                        |
| `page_size`             | int    | 10                        | (可选) 每页数量，默认10                                                   |
| `model_name_search`     | string | "RayTracer"               | (可选) 模型名称模糊搜索                                                   |
| `model_type`            | string | "large_scale"             | (可选) 模型类型 (e.g., "large_scale", "situation_awareness", "small_scale") |
| `frequency_bands`       | string | "2.4GHz,5.9GHz"           | (可选) 适用频段，逗号分隔，用于匹配模型支持的频段列表 (部分匹配即可)        |
| `application_scenarios` | string | "urban,highway"           | (可选) 应用场景，逗号分隔，用于匹配模型支持的应用场景列表 (部分匹配即可)      |

**响应结构**:
```json
{
  "message": "success",
  "code": "200",
  "data": {
    "models": [
      {
        "model_uuid": "uuid-model-001",
        "model_name": "RayTracer-Pro",
        "model_type": "large_scale",
        "frequency_bands": ["2.4GHz", "5.8GHz", "28GHz"],
        "application_scenarios": ["urban_macro", "indoor_office"],
        "update_time": "2023-10-26T10:00:00Z",
        "can_be_used_for_validation": true
      }
      // ... more models
    ],
    "pagination": {
      "current_page": 1,
      "page_size": 10,
      "total_items": 100,
      "total_pages": 10
    }
  }
}
```
**`models` 元素字段说明**:
| 字段名                   | 类型    | 示例                                      | 备注                                     |
|--------------------------|---------|-------------------------------------------|------------------------------------------|
| `model_uuid`             | string  | "uuid-model-001"                          | 模型唯一标识                             |
| `model_name`             | string  | "RayTracer-Pro"                           | 模型名称                                 |
| `model_type`             | string  | "large_scale"                             | 模型类型 ("large_scale", "situation_awareness", "small_scale") |
| `frequency_bands`        | array   | `["2.4GHz", "5.8GHz", "28GHz"]`           | 适用频段列表                             |
| `application_scenarios`  | array   | `["urban_macro", "indoor_office"]`        | 应用场景列表                             |
| `update_time`            | string  | "2023-10-26T10:00:00Z"                    | 更新时间 (ISO 8601)                      |
| `can_be_used_for_validation`| boolean | true                                      | 是否有对应的数据集可用于模型验证          |

### **获取单个模型详情 (Get Model Details for Edit)**
**接口名称**: `getModelDetails()`
**请求方法**: `GET`
**路径**: `/api/v1/models/{model_uuid}`

**描述**: 获取指定模型的详细信息，用于编辑表单填充。

**请求参数 (路径)**:
| 参数名        | 类型   | 示例             | 备注                   |
|---------------|--------|------------------|------------------------|
| `model_uuid`  | string | "uuid-model-001" | 模型唯一标识 (路径参数) |

**响应结构**:
```json
{
  "message": "success",
  "code": "200",
  "data": {
    "model_uuid": "uuid-model-001",
    "model_name": "RayTracer-Pro",
    "model_type": "large_scale",
    "frequency_bands": ["2.4GHz", "5.8GHz"],
    "application_scenarios": ["urban_macro"],
    "model_description": "基于射线追踪的高精度模型。",
    "model_doc_filename": "RayTracer-Pro_doc.md",
    "tiff_image_filename": "urban_sample.tiff",
    "dataset_for_validation_filename": "validation_data_raytracer.zip",
    "update_time": "2023-10-26T10:00:00Z"
  }
}
```
**字段说明**:
| 字段名                            | 类型   | 示例                                 | 备注                                           |
|-----------------------------------|--------|--------------------------------------|------------------------------------------------|
| `model_uuid`                      | string | "uuid-model-001"                     | 模型唯一标识                                   |
| `model_name`                      | string | "RayTracer-Pro"                      | 模型名称                                       |
| `model_type`                      | string | "large_scale"                        | 模型类型                                       |
| `frequency_bands`                 | array  | `["2.4GHz", "5.8GHz"]`               | 适用频段列表                                   |
| `application_scenarios`           | array  | `["urban_macro"]`                    | 应用场景列表                                   |
| `model_description`               | string | "基于射线追踪的高精度模型。"            | 模型描述                                       |
| `model_doc_filename`              | string | "RayTracer-Pro_doc.md"               | 模型说明文档文件名 (用于显示)                  |
| `tiff_image_filename`             | string | "urban_sample.tiff"                  | 相关图像文件名 (若模型导入时包含, 用于显示)    |
| `dataset_for_validation_filename` | string | "validation_data_raytracer.zip"    | 关联的验证数据集文件名 (若有, 用于显示)        |
| `update_time`                     | string | "2023-10-26T10:00:00Z"               | 更新时间                                       |


### **导入/创建新模型 (Import/Create New Model)**
**接口名称**: `importModel()`
**请求方法**: `POST`
**路径**: `/api/v1/models`
**Content-Type**: `multipart/form-data`

**描述**: 导入新模型或创建模型条目，包括模型文件、文档等。

**请求体 (form-data)**:
| 字段名                  | 类型       | 示例                                  | 备注                                                                 |
|-------------------------|------------|---------------------------------------|----------------------------------------------------------------------|
| `model_name`            | string     | "NewGen Channel Model"                | 模型名称 (限10中文字符或等效)                                          |
| `model_type`            | string     | "small_scale"                         | 模型类型 (enum: "large_scale", "situation_awareness", "small_scale") |
| `frequency_bands`       | string     | "[\"28GHz\", \"70GHz\"]"                | JSON字符串数组，适用频段                                             |
| `application_scenarios` | string     | "[\"indoor_factory\", \"V2X\"]"       | JSON字符串数组，应用场景                                             |
| `model_description`     | string     | "下一代小尺度信道模型，支持毫米波。"     | 模型描述                                                             |
| `model_zip_file`        | file       | (binary data)                         | 包含模型本身、说明文档(markdown)、相关图像(tiff)等的ZIP压缩包        |
| `dataset_for_validation_zip_file` | file | (可选, binary data)                | (可选) 与此模型关联的验证用数据集压缩包 (包含实测数据等)              |


**响应结构**:
```json
{
  "message": "Model imported successfully.",
  "code": "201",
  "data": {
    "model_uuid": "uuid-model-new-001",
    "model_name": "NewGen Channel Model"
  }
}
```

### **更新模型信息 (Update Model Information)**
**接口名称**: `updateModel()`
**请求方法**: `PUT`
**路径**: `/api/v1/models/{model_uuid}`
**Content-Type**: `multipart/form-data` (if files are updated), or `application/json` (if only metadata)

**描述**: 更新现有模型的信息。

**请求参数 (路径)**:
| 参数名        | 类型   | 示例             | 备注           |
|---------------|--------|------------------|----------------|
| `model_uuid`  | string | "uuid-model-001" | 模型唯一标识   |

**请求体 (form-data or JSON, all fields optional)**:
与创建模型类似，只包含需要更新的字段。
*   如果 `model_zip_file` 或 `dataset_for_validation_zip_file` 作为文件在 `multipart/form-data` 中提供，它们将替换现有文件。
*   若要解除验证数据集的关联，可在JSON中发送 `"dataset_for_validation_zip_file": null`。

**示例 JSON 请求体 (不更新文件时)**:
```json
{
  "model_name": "NewGen Channel Model v2",
  "model_description": "更新后的描述。",
  "frequency_bands": ["28GHz", "70GHz", "140GHz"]
}
```

**响应结构**:
```json
{
  "message": "Model updated successfully.",
  "code": "200",
  "data": {
    "model_uuid": "uuid-model-001"
  }
}
```

### **删除模型 (Delete Model)**
**接口名称**: `deleteModel()`
**请求方法**: `DELETE`
**路径**: `/api/v1/models/{model_uuid}`

**描述**: 删除指定的模型。

**请求参数 (路径)**:
| 参数名        | 类型   | 示例             | 备注           |
|---------------|--------|------------------|----------------|
| `model_uuid`  | string | "uuid-model-001" | 模型唯一标识   |

**响应结构**:
```json
{
  "message": "Model deleted successfully.",
  "code": "200", // Or 204 No Content
  "data": null
}
```

### **获取模型筛选条件选项 (Get Model Filter Options)**
**接口名称**: `getModelFilterOptions()`
**请求方法**: `GET`
**路径**: `/api/v1/models/filter_options`

**描述**: 获取模型广场筛选器可用的选项列表。

**响应结构**:
```json
{
  "message": "success",
  "code": "200",
  "data": {
    "model_types": [
      {"value": "large_scale", "label": "大尺度模型"},
      {"value": "situation_awareness", "label": "态势感知模型"},
      {"value": "small_scale", "label": "小尺度模型"}
    ],
    "frequency_bands": [
      {"value": "sub_6GHz", "label": "Sub-6GHz"},
      {"value": "2.4GHz", "label": "2.4GHz"},
      {"value": "5.9GHz", "label": "5.9GHz"},
      {"value": "28GHz", "label": "28GHz"},
      {"value": "60GHz", "label": "60GHz"}
    ],
    "application_scenarios": [
      {"value": "urban_macro", "label": "城市宏"},
      {"value": "indoor_office", "label": "室内办公"},
      {"value": "highway", "label": "高速公路"},
      {"value": "v2x", "label": "V2X"}
    ]
  }
}
```
**说明**: `frequency_bands` 和 `application_scenarios` 的列表可能基于预定义值，也可能动态地从现有模型的数据中填充。

---

## **模型详情介绍 (Model Detail Introduction)**

### **获取模型分类及简要列表 (Get Grouped Model List)**
**接口名称**: `getGroupedModels()`
**请求方法**: `GET`
**路径**: `/api/v1/models/grouped_list`

**描述**: 获取按类型分组的模型列表，用于详情页左侧导航。

**响应结构**:
```json
{
  "message": "success",
  "code": "200",
  "data": [
    {
      "group_name": "大尺度模型",
      "group_id": "large_scale",
      "models": [
        { "model_uuid": "uuid-model-001", "model_name": "RayTracer-Pro" },
        { "model_uuid": "uuid-model-004", "model_name": "StatisticalModel-A" }
      ]
    },
    {
      "group_name": "态势感知模型",
      "group_id": "situation_awareness",
      "models": [
        { "model_uuid": "uuid-model-002", "model_name": "Plana3.0-Urban" }
      ]
    },
    {
      "group_name": "小尺度模型",
      "group_id": "small_scale",
      "models": [
        { "model_uuid": "uuid-model-003", "model_name": "MmWave-PDP-Gen" }
      ]
    }
  ]
}
```

### **获取模型详细介绍内容 (Get Model Full Details)**
**接口名称**: `getModelFullDetails()`
**请求方法**: `GET`
**路径**: `/api/v1/models/{model_uuid}/details`

**描述**: 获取指定模型的完整详细介绍，包括Markdown文档内容、相关案例等。模型文档内容从导入的ZIP包中提取。

**请求参数 (路径)**:
| 参数名        | 类型   | 示例             | 备注           |
|---------------|--------|------------------|----------------|
| `model_uuid`  | string | "uuid-model-001" | 模型唯一标识   |

**响应结构**:
```json
{
  "message": "success",
  "code": "200",
  "data": {
    "model_uuid": "uuid-model-001",
    "model_name": "RayTracer-Pro",
    "model_type": "large_scale",
    "model_description": "基于射线追踪的高精度模型。",
    "frequency_bands": ["2.4GHz", "5.8GHz"],
    "application_scenarios": ["urban_macro"],
    "update_time": "2023-10-26T10:00:00Z",
    "markdown_doc_content": "# RayTracer-Pro\n\n## 概述\n这是一个...",
    "practice_cases_preview": [
      {
        "case_dir_name": "case_folder_urban_raytracing",
        "case_img": "/storage/best_cases/case_folder_urban_raytracing/thumbnail.jpg",
        "case_title": "城市宏站覆盖分析 - RayTracer-Pro应用",
        "case_type": "simulation"
      }
    ],
    "overview_summary": "RayTracer-Pro 是一款先进的射线追踪引擎..."
  }
}
```
**字段说明**:
| 字段名                   | 类型   | 示例                               | 备注                                                         |
|--------------------------|--------|------------------------------------|--------------------------------------------------------------|
| `model_uuid`             | string | "uuid-model-001"                   | 模型唯一标识                                                 |
| `model_name`             | string | "RayTracer-Pro"                    | 模型名称                                                     |
| `model_type`             | string | "large_scale"                      | 模型类型                                                     |
| `model_description`      | string | "基于射线追踪的高精度模型。"        | 模型简短描述                                                 |
| `frequency_bands`        | array  | `["2.4GHz", "5.8GHz"]`             | 适用频段列表                                                 |
| `application_scenarios`  | array  | `["urban_macro"]`                  | 应用场景列表                                                 |
| `update_time`            | string | "2023-10-26T10:00:00Z"             | 更新时间                                                     |
| `markdown_doc_content`   | string | "# RayTracer-Pro\n..."             | Markdown格式的详细文档内容                                   |
| `practice_cases_preview` | array  | 见下                               | 关联的实践案例预览 (从首页案例中筛选与此模型相关的)            |
| `overview_summary`       | string | "RayTracer-Pro 是一款..."          | 概述总结 (可能从MD文档中提取或单独字段)                    |

**`practice_cases_preview` 元素字段说明**:
| 字段名          | 类型   | 示例                                        | 备注                                  |
|-----------------|--------|---------------------------------------------|---------------------------------------|
| `case_dir_name` | string | "case_folder_urban_raytracing"              | 案例目录名 (用于链接到在线推演此案例) |
| `case_img`      | string | "/storage/best_cases/.../thumbnail.jpg"     | 案例图片路径                          |
| `case_title`    | string | "城市宏站覆盖分析 - RayTracer-Pro应用"      | 案例标题                              |
| `case_type`     | string | "simulation"                                | 案例类型                              |

---

## **信道数据 (Channel Data Management)**

### **获取信道数据集列表 (Get Channel Dataset List)**
**接口名称**: `getChannelDatasets()`
**请求方法**: `GET`
**路径**: `/api/v1/channel_datasets`

**描述**: 获取已导入的信道数据集列表，支持筛选和分页。

**请求参数**:
| 参数名                  | 类型   | 示例                      | 备注                                                                      |
|-------------------------|--------|---------------------------|---------------------------------------------------------------------------|
| `page`                  | int    | 1                         | (可选) 页码                                                               |
| `page_size`             | int    | 10                        | (可选) 每页数量                                                           |
| `dataset_name_search`   | string | "Urban"                   | (可选) 数据集名称模糊搜索                                                 |
| `data_type`             | string | "real_measurement"        | (可选) 数据类型: "real_measurement" (实测数据), "simulation" (仿真数据)   |
| `location_description_search` | string | "北京市海淀区"      | (可选) 地点描述模糊搜索                                                   |
| `center_frequency_mhz`  | float  | 6000                      | (可选) 中心频率 (MHz) - 精确匹配或范围查询                                  |
| `applicable_task_type`  | string | "single_point_prediction" | (可选) 适用任务类型 (e.g., "single_point_prediction", "situation_prediction", "small_scale_prediction") |

**响应结构**:
```json
{
  "message": "success",
  "code": "200",
  "data": {
    "datasets": [
      {
        "dataset_uuid": "ds-uuid-001",
        "dataset_name": "北京交通大学主校区环线实测",
        "data_type": "real_measurement",
        "location_description": "北京市海淀区北京交通大学",
        "center_frequency_mhz": 5900.0,
        "bandwidth_mhz": 100.0,
        "data_volume_groups": 584,
        "applicable_task_type": "single_point_prediction",
        "update_time": "2023-11-01T14:30:00Z",
        "file_name": "bjtu_campus_drive_test.zip"
      }
      // ... more datasets
    ],
    "pagination": {
      "current_page": 1,
      "page_size": 10,
      "total_items": 50,
      "total_pages": 5
    }
  }
}
```
**`datasets` 元素字段说明**:
| 字段名                   | 类型   | 示例                             | 备注                                                        |
|--------------------------|--------|----------------------------------|-------------------------------------------------------------|
| `dataset_uuid`           | string | "ds-uuid-001"                    | 数据集唯一标识                                              |
| `dataset_name`           | string | "北京交通大学主校区环线实测"       | 数据集名称                                                  |
| `data_type`              | string | "real_measurement"               | 数据类型 ("real_measurement", "simulation")                 |
| `location_description`   | string | "北京市海淀区北京交通大学"       | 地点描述                                                    |
| `center_frequency_mhz`   | float  | 5900.0                           | 中心频率 (MHz)                                              |
| `bandwidth_mhz`          | float  | 100.0                            | 带宽 (MHz)                                                  |
| `data_volume_groups`     | int    | 584                              | 数据组数                                                    |
| `applicable_task_type`   | string | "single_point_prediction"        | 适用任务类型 ("single_point_prediction", "situation_prediction", "small_scale_prediction") |
| `update_time`            | string | "2023-11-01T14:30:00Z"           | 更新时间 (ISO 8601)                                         |
| `file_name`              | string | "bjtu_campus_drive_test.zip"     | 上传时的原始文件名                                          |

### **导入信道数据集 (Import Channel Dataset)**
**接口名称**: `importChannelDataset()`
**请求方法**: `POST`
**路径**: `/api/v1/channel_datasets`
**Content-Type**: `multipart/form-data`

**描述**: 上传并导入新的信道数据集。

**请求体 (form-data)**:
| 字段名                 | 类型   | 示例                             | 备注                                        |
|------------------------|--------|----------------------------------|---------------------------------------------|
| `dataset_name`         | string | "城市峡谷场景数据集"             | 数据集名称 (限25字符)                       |
| `data_type`            | string | "simulation"                     | 数据类型 ("real_measurement", "simulation") |
| `location_description` | string | "上海市浦东新区陆家嘴"             | 地点描述                                    |
| `center_frequency_mhz` | float  | 28000.0                          | 中心频率 (MHz, 最多2位小数)                 |
| `bandwidth_mhz`        | float  | 400.0                            | 带宽 (MHz, 最多2位小数)                     |
| `data_volume_groups`   | int    | 1200                             | 数据组数 (整数)                             |
| `applicable_task_type` | string | "situation_prediction"           | 适用任务类型                                |
| `dataset_file`         | file   | (binary data of ZIP or Excel)    | 数据集文件 (ZIP或Excel，根据样例格式)       |

**响应结构**:
```json
{
  "message": "Dataset imported successfully.",
  "code": "201",
  "data": {
    "dataset_uuid": "ds-uuid-new-002",
    "dataset_name": "城市峡谷场景数据集"
  }
}
```

### **获取单个信道数据集信息 (Get Channel Dataset Details for Edit)**
**接口名称**: `getChannelDatasetDetails()`
**请求方法**: `GET`
**路径**: `/api/v1/channel_datasets/{dataset_uuid}`

**描述**: 获取指定数据集的详细信息，用于编辑表单。

**请求参数 (路径)**:
| 参数名         | 类型   | 示例          | 备注             |
|----------------|--------|---------------|------------------|
| `dataset_uuid` | string | "ds-uuid-001" | 数据集唯一标识   |

**响应结构 (字段与列表中的单个dataset对象字段一致，额外增加下载链接)**:
```json
{
  "message": "success",
  "code": "200",
  "data": {
    "dataset_uuid": "ds-uuid-001",
    "dataset_name": "北京交通大学主校区环线实测",
    "data_type": "real_measurement",
    "location_description": "北京市海淀区北京交通大学",
    "center_frequency_mhz": 5900.0,
    "bandwidth_mhz": 100.0,
    "data_volume_groups": 584,
    "applicable_task_type": "single_point_prediction",
    "update_time": "2023-11-01T14:30:00Z",
    "file_name": "bjtu_campus_drive_test.zip",
    "file_download_url": "/api/v1/channel_datasets/ds-uuid-001/download"
  }
}
```
**`file_download_url`**: (可选) 用于下载已上传的文件。

### **更新信道数据集元数据 (Update Channel Dataset Metadata)**
**接口名称**: `updateChannelDataset()`
**请求方法**: `PUT`
**路径**: `/api/v1/channel_datasets/{dataset_uuid}`
**Content-Type**: `application/json` (if only metadata) or `multipart/form-data` (if file is also updated)

**描述**: 更新现有信道数据集的元数据。如果需要替换文件，则使用 `multipart/form-data` 并包含 `dataset_file`。

**请求参数 (路径)**:
| 参数名         | 类型   | 示例          | 备注             |
|----------------|--------|---------------|------------------|
| `dataset_uuid` | string | "ds-uuid-001" | 数据集唯一标识   |

**请求体 (JSON or form-data, all fields optional for metadata update)**:
所有字段均为可选，只传递需要更新的字段。
**示例 JSON 请求体 (仅更新元数据)**:
```json
{
  "dataset_name": "更新后的数据集名称",
  "data_type": "simulation",
  "location_description": "新的地点描述",
  "center_frequency_mhz": 6000.0,
  "bandwidth_mhz": 200.0,
  "data_volume_groups": 600,
  "applicable_task_type": "small_scale_prediction"
}
```
若使用 `multipart/form-data` 且包含 `dataset_file` 字段，则会替换原有文件。

**响应结构**:
```json
{
  "message": "Dataset updated successfully.",
  "code": "200",
  "data": {
    "dataset_uuid": "ds-uuid-001"
  }
}
```

### **删除信道数据集 (Delete Channel Dataset)**
**接口名称**: `deleteChannelDataset()`
**请求方法**: `DELETE`
**路径**: `/api/v1/channel_datasets/{dataset_uuid}`

**描述**: 删除指定的信道数据集。

**请求参数 (路径)**:
| 参数名         | 类型   | 示例          | 备注             |
|----------------|--------|---------------|------------------|
| `dataset_uuid` | string | "ds-uuid-001" | 数据集唯一标识   |

**响应结构**:
```json
{
  "message": "Dataset deleted successfully.",
  "code": "200", // Or 204 No Content
  "data": null
}
```

### **下载数据集上传样例 (Download Dataset Upload Template)**
**接口名称**: `getDatasetUploadTemplate()`
**请求方法**: `GET`
**路径**: `/api/v1/channel_datasets/upload_template`

**描述**: 下载用于上传信道数据的Excel模板文件。模板内容可能根据任务类型不同而不同。

**请求参数**:
| 参数名        | 类型   | 示例                                  | 备注                                                     |
|---------------|--------|---------------------------------------|----------------------------------------------------------|
| `task_type`   | string | "single_point_prediction_link_mode" | (可选) 指定任务类型获取对应格式模板。具体枚举值待定。 e.g., "single_point_prediction_discrete_mode", "single_point_prediction_link_mode", "situation_prediction", "small_scale_prediction"  |

**响应**: Excel文件 (`application/vnd.ms-excel` or `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`)

---

## **模型验证 (Model Validation / PK)**

### **获取验证任务类型列表 (Get Validation Task Types)**
**接口名称**: `getValidationTaskTypes()`
**请求方法**: `GET`
**路径**: `/api/v1/validation/task_types`

**描述**: 获取可用于模型验证的任务类型。
**响应结构**:
```json
{
  "message": "success",
  "code": "200",
  "data": [
    { "id": "single_point_discrete", "name": "单点预测-单点模式验证" },
    { "id": "single_point_link", "name": "单点预测-链路模式验证" },
    { "id": "situation", "name": "态势预测验证" },
    { "id": "small_scale", "name": "小尺度预测验证" }
  ]
}
```

### **获取适用于验证的数据集列表 (Get Datasets for Validation)**
**接口名称**: `getValidationDatasets()`
**请求方法**: `GET`
**路径**: `/api/v1/validation/datasets`

**描述**: 根据选择的验证任务类型，获取可用的信道数据集（必须是实测数据类型）。
**请求参数**:
| 参数名       | 类型   | 示例                      | 备注                                              |
|--------------|--------|---------------------------|---------------------------------------------------|
| `task_type`  | string | "single_point_link"       | 验证任务类型ID (from `getValidationTaskTypes`)    |

**响应结构**:
```json
{
  "message": "success",
  "code": "200",
  "data": [
    {
      "dataset_uuid": "ds-uuid-001",
      "dataset_name": "北京高速公路实测数据",
      "location_description": "京沪高速北京段",
      "center_frequency_mhz": 3500.0,
      "applicable_task_type": "single_point_link"
    }
    // ... more datasets suitable for the task_type and are 'real_measurement'
  ]
}
```
**字段说明**:
| 字段名                   | 类型   | 示例                      | 备注                                      |
|--------------------------|--------|---------------------------|-------------------------------------------|
| `dataset_uuid`           | string | "ds-uuid-001"             | 数据集唯一标识                            |
| `dataset_name`           | string | "北京高速公路实测数据"    | 数据集名称                                |
| `location_description`   | string | "京沪高速北京段"          | 地点描述                                  |
| `center_frequency_mhz`   | float  | 3500.0                    | 中心频率 (MHz)                            |
| `applicable_task_type`   | string | "single_point_link"       | 确保数据集与任务类型匹配 (冗余信息供前端) |

### **获取适用于验证的模型列表 (Get Models for Validation)**
**接口名称**: `getValidationModels()`
**请求方法**: `GET`
**路径**: `/api/v1/validation/models`

**描述**: 根据选择的验证任务类型和数据集，获取可参与验证的模型。
**请求参数**:
| 参数名         | 类型   | 示例                      | 备注                                                     |
|----------------|--------|---------------------------|----------------------------------------------------------|
| `task_type`    | string | "single_point_link"       | 验证任务类型ID                                           |
| `dataset_uuid` | string | "ds-uuid-001"             | 所选数据集ID (确保模型与数据及任务类型兼容)                |

**响应结构**:
```json
{
  "message": "success",
  "code": "200",
  "data": [
    { "model_uuid": "uuid-model-001", "model_name": "RayTracer-Pro" },
    { "model_uuid": "uuid-model-005", "model_name": "COST231-Hata" }
    // ... more models suitable for the task_type and dataset
  ]
}
```

### **创建模型验证任务 (Create Model Validation Task)**
**接口名称**: `createValidationTask()`
**请求方法**: `POST`
**路径**: `/api/v1/validation/tasks`

**描述**: 提交一个模型验证（PK）任务。
**请求体**:
```json
{
  "validation_task_name": "京沪高速模型对比验证",
  "task_type": "single_point_link",
  "dataset_uuid": "ds-uuid-001",
  "model_uuids": ["uuid-model-001", "uuid-model-005"],
  "param_config": {
    "modulation_mode": "QPSK",
    "modulation_order": 4
  }
}
```
**字段说明**:
| 字段名                 | 类型   | 示例                               | 备注                                                     |
|------------------------|--------|------------------------------------|----------------------------------------------------------|
| `validation_task_name` | string | "京沪高速模型对比验证"             | (可选) 用户自定义任务名                                  |
| `task_type`            | string | "single_point_link"                | 验证任务类型ID (from `getValidationTaskTypes`)           |
| `dataset_uuid`         | string | "ds-uuid-001"                      | 数据集唯一标识                                           |
| `model_uuids`          | array  | `["uuid-model-001", "uuid-model-005"]` | 要对比的模型UUID列表                                     |
| `param_config`         | object | (可选)                             | 仅当 `task_type` 为 "small_scale" 时需要, 包含小尺度预测任务所需额外参数 (如果数据集本身不包含这些) |
| `param_config.modulation_mode` | string | "QPSK"                    | (small_scale) 调制方式                                   |
| `param_config.modulation_order`| int    | 4                         | (small_scale) 调制阶数                                   |

**响应结构**:
```json
{
  "message": "Validation task created successfully.",
  "code": "201",
  "data": {
    "validation_task_uuid": "val-task-uuid-001"
  }
}
```

### **获取模型验证任务状态和结果 (Get Model Validation Task Status & Results)**
**接口名称**: `getValidationTaskResults()`
**请求方法**: `GET`
**路径**: `/api/v1/validation/tasks/{validation_task_uuid}`

**描述**: 获取指定模型验证任务的当前状态和最终对比结果。
**请求参数 (路径)**:
| 参数名                | 类型   | 示例                | 备注                     |
|-----------------------|--------|---------------------|--------------------------|
| `validation_task_uuid`| string | "val-task-uuid-001" | 模型验证任务唯一标识     |

**通用响应结构框架**:
```json
{
  "message": "success",
  "code": "200",
  "data": {
    "validation_task_uuid": "val-task-uuid-001",
    "validation_task_name": "京沪高速模型对比验证",
    "task_type": "single_point_link",
    "dataset_name": "北京高速公路实测数据",
    "status": "COMPLETED",
    "error_message": null,
    "actual_data": {
      // 结构取决于 task_type
    },
    "model_comparison_results": [
      // 结构取决于 task_type
    ]
  }
}
```
**通用字段说明**:
| 字段名                 | 类型   | 示例                      | 备注                                                                       |
|------------------------|--------|---------------------------|----------------------------------------------------------------------------|
| `validation_task_uuid` | string | "val-task-uuid-001"       | 模型验证任务唯一标识                                                       |
| `validation_task_name` | string | "京沪高速模型对比验证"    | 用户定义的任务名称                                                         |
| `task_type`            | string | "single_point_link"       | 验证任务类型 (e.g., "single_point_discrete", "situation", "small_scale") |
| `dataset_name`         | string | "北京高速公路实测数据"    | 使用的数据集名称                                                           |
| `status`               | string | "COMPLETED"               | 任务状态 ("PENDING", "IN_PROGRESS", "COMPLETED", "FAILED", "PARTIAL_COMPLETE") |
| `error_message`        | string | null                      | 如果状态是 FAILED，则包含错误信息                                            |
| `actual_data`          | object |                           | 从数据集中提取的用于对比的实测数据，结构依 `task_type` 而定                |
| `model_comparison_results`| array |                        | 每个模型的对比结果数组，其中元素结构依 `task_type` 而定                    |

#### **`actual_data` 和 `model_comparison_results` 结构 - for `task_type: "single_point_link"`**

**`actual_data` (for "single_point_link")**:
```json
{
  "path_loss_curve": [
    {"distance_m": 0, "pos": {"lat":..., "lon":...}, "real_pl_db": 89.0},
    {"distance_m": 50, "pos": {"lat":..., "lon":...}, "real_pl_db": 93.5}
    // ...
  ]
}
```
**`model_comparison_results` 元素 (for "single_point_link")**:
```json
{
  "model_uuid": "uuid-model-001",
  "model_name": "RayTracer-Pro",
  "status": "COMPLETED", // "COMPLETED", "FAILED" (针对此模型)
  "error_message": null,
  "overall_rmse_db": 4.5,
  "predicted_path_loss_curve": [ // 与 actual_data.path_loss_curve 中的 distance_m/pos 对齐
    { "distance_m": 0, "pos": {"lat":..., "lon":...}, "predicted_pl_db": 90.1 },
    { "distance_m": 50, "pos": {"lat":..., "lon":...}, "predicted_pl_db": 95.3 }
    // ...
  ]
}
```

#### **`actual_data` 和 `model_comparison_results` 结构 - for `task_type: "single_point_discrete"`**

**`actual_data` (for "single_point_discrete")**:
```json
{
  "points": [
    {"point_id_in_dataset": "RX1", "tx_pos": {...}, "rx_pos": {...}, "real_pl_db": 100.0},
    {"point_id_in_dataset": "RX2", "tx_pos": {...}, "rx_pos": {...}, "real_pl_db": 105.3}
  ]
}
```
**`model_comparison_results` 元素 (for "single_point_discrete")**:
```json
{
  "model_uuid": "uuid-model-001",
  "model_name": "RayTracer-Pro",
  "status": "COMPLETED",
  "overall_rmse_db": 3.1,
  "point_predictions": [ // 与 actual_data.points 中的点对齐
    {"point_id_in_dataset": "RX1", "predicted_pl_db": 102.5, "error_db": 2.5},
    {"point_id_in_dataset": "RX2", "predicted_pl_db": 104.0, "error_db": -1.3}
  ]
}
```

#### **`actual_data` 和 `model_comparison_results` 结构 - for `task_type: "situation"`**

**`actual_data` (for "situation")**:
```json
{
  "heatmap_data_type": "grid", // or "geojson_url"
  "grid_origin": { "lat": ..., "lon": ... },
  "cell_size_deg": { "lat_delta": ..., "lon_delta": ... }, // 或 cell_size_m
  "rows": ..., "cols": ...,
  "values": [[...],[...]], // 实测热力图值
  "value_unit": "dB"
}
```
**`model_comparison_results` 元素 (for "situation")**:
```json
{
  "model_uuid": "uuid-model-00A",
  "model_name": "SituationModelAlpha",
  "status": "COMPLETED",
  "comparison_metrics": {
    "heatmap_rmse_db": 5.8,
    "coverage_accuracy_percent": 85.2
  },
  "predicted_heatmap_data": { // 与 actual_data.heatmap_data 结构相同
    "heatmap_data_type": "grid",
    "grid_origin": { "lat": ..., "lon": ... },
    "cell_size_deg": { "lat_delta": ..., "lon_delta": ... },
    "rows": ..., "cols": ...,
    "values": [[...],[...]],
    "value_unit": "dB"
  }
  // Or: "predicted_heatmap_data_url": "/storage/validation_results/..."
}
```

#### **`actual_data` 和 `model_comparison_results` 结构 - for `task_type: "small_scale"`**

**`actual_data` (for "small_scale")**:
```json
{
   "pdp_data": { /* 实测PDP数据结构, 类似在线推演结果 */ },
   "ber_snr_data": { /* 实测BER/SNR数据结构, 类似在线推演结果 */ }
}
```
**`model_comparison_results` 元素 (for "small_scale")**:
```json
{
  "model_uuid": "uuid-model-00B",
  "model_name": "SmallScaleAdvanced",
  "status": "COMPLETED",
  "pdp_comparison_metrics": {
    "average_delay_spread_error_ns": 5.2,
    "rmse_power_db_per_delay_bin": [2.1, 3.0, 1.5, ...]
  },
  "ber_snr_comparison_metrics": {
    "ber_rmse_at_snr_points": [
       {"snr_db": 10, "rmse_ber": 0.0015},
       {"snr_db": 15, "rmse_ber": 0.0008}
    ]
  },
  "predicted_pdp_data": { /* 预测PDP数据结构, 与 actual_data.pdp_data 类似 */ },
  "predicted_ber_snr_data": { /* 预测BER/SNR数据结构, 与 actual_data.ber_snr_data 类似 */ }
  // Or URLs to these data files
}
```

---