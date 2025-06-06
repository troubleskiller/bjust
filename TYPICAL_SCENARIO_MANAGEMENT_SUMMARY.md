# 典型场景管理功能实现总结

## 功能概述

成功实现了典型场景管理功能，允许用户动态添加新的典型场景。该功能支持用户上传input CSV文件、指定tif图名称和选择预测类型来创建自定义的典型场景。

## 预测类型支持

系统支持三种预测类型：
- **单点预测** (single_point) - 针对特定点位的信号预测
- **动态感知** (dynamic_sensing) - 实时环境感知和预测
- **小尺度预测** (small_scale) - 小范围精细化预测

## 核心功能

### 1. 获取预测类型列表
- **接口**: `GET /api/v1/typical_scenarios/prediction_types`
- **功能**: 获取系统支持的所有预测类型

### 2. 添加典型场景
- **接口**: `POST /api/v1/typical_scenarios`
- **功能**: 用户提供场景名称、预测类型、tif图名称和input CSV文件来创建新的典型场景
- **存储结构**: 在`storage/typical_scenarios/{预测类型前缀}_{随机UUID}/`目录下创建：
  - `input.csv` - 场景配置数据文件
  - `scenario_metadata.json` - 元信息文件，记录tif图映射和其他信息

### 3. 列出所有典型场景  
- **接口**: `GET /api/v1/typical_scenarios`
- **功能**: 获取所有可用的典型场景列表，支持按预测类型分组展示

### 4. 按预测类型获取典型场景
- **接口**: `GET /api/v1/typical_scenarios?prediction_type={预测类型}`
- **功能**: 获取指定预测类型的典型场景列表
- **参数**: prediction_type (可选) - 预测类型过滤器

### 5. 获取场景详细信息
- **接口**: `GET /api/v1/typical_scenarios/{场景名称、文件夹名称或UUID}`
- **功能**: 获取指定典型场景的详细信息，包括文件列表、创建时间等

### 6. 删除典型场景
- **接口**: `DELETE /api/v1/typical_scenarios/{场景名称、文件夹名称或UUID}`
- **功能**: 删除指定的典型场景及其所有文件

## 文件结构

### 目录布局
```
storage/typical_scenarios/
├── single_point_{UUID1}/
│   ├── input.csv              # 场景配置CSV文件
│   └── scenario_metadata.json # 元信息文件
├── dynamic_sensing_{UUID2}/
│   ├── input.csv
│   └── scenario_metadata.json
├── small_scale_{UUID3}/
│   ├── input.csv
│   └── scenario_metadata.json
└── ...
```

### 元信息文件格式
```json
{
  "scenario_uuid": "生成的UUID",
  "folder_name": "预测类型前缀_UUID",
  "scenario_name": "场景名称",
  "prediction_type": "单点预测",
  "prediction_type_code": "single_point",
  "tif_image_name": "对应的tif图名称",
  "input_file": "input.csv",
  "input_file_type": "csv",
  "created_at": "2024-01-01T12:00:00",
  "description": "典型场景: 场景名称 (单点预测)",
  "tif_mapping": {
    "source_tif": "tif图名称",
    "scenario_type": "custom_added"
  }
}
```

## 新增文件清单

### 1. 服务层
- **文件**: `app/service/typical_scenario_service.py`
- **新增映射**: `PREDICTION_TYPE_MAPPING` - 预测类型中英文映射
- **功能**:
  - `get_available_prediction_types()` - 获取可用预测类型列表
  - `validate_csv_file()` - CSV文件格式验证
  - `add_typical_scenario_service()` - 添加典型场景（支持预测类型）
  - `find_scenario_by_name()` - 通过场景名称查找文件夹名称
  - `get_typical_scenario_info_service()` - 获取场景信息（支持多种标识符）
  - `list_all_typical_scenarios_service()` - 列出所有场景（支持按类型分组）
  - `list_typical_scenarios_by_type_service()` - 按预测类型列出场景
  - `delete_typical_scenario_service()` - 删除场景（支持多种标识符）

### 2. 路由层
- **文件**: `app/route/typical_scenario_route.py`
- **功能**: 提供完整的RESTful API接口，支持预测类型管理

### 3. 应用初始化
- **文件**: `app/__init__.py`
- **修改**: 注册典型场景管理蓝图

### 4. 测试脚本
- **文件**: `test_typical_scenario_management.py`
- **功能**: 完整测试所有API功能，包括预测类型测试

## API使用示例

### 获取预测类型列表
```bash
curl -X GET http://localhost:9001/api/v1/typical_scenarios/prediction_types
```

### 添加典型场景
```bash
curl -X POST http://localhost:9001/api/v1/typical_scenarios \
  -F "scenario_name=新工业园区" \
  -F "prediction_type=单点预测" \
  -F "tif_image_name=nanjing" \
  -F "input_file=@scenario_config.csv"
```

### 获取场景列表（支持按类型分组）
```bash
curl -X GET http://localhost:9001/api/v1/typical_scenarios
```

### 按预测类型获取场景列表
```bash
# 获取单点预测类型的场景
curl -X GET "http://localhost:9001/api/v1/typical_scenarios?prediction_type=单点预测"

# 获取动态感知类型的场景  
curl -X GET "http://localhost:9001/api/v1/typical_scenarios?prediction_type=动态感知"

# 获取小尺度预测类型的场景
curl -X GET "http://localhost:9001/api/v1/typical_scenarios?prediction_type=小尺度预测"
```

### 获取场景详情（支持多种标识符）
```bash
# 使用场景名称
curl -X GET http://localhost:9001/api/v1/typical_scenarios/新工业园区
# 使用文件夹名称  
curl -X GET http://localhost:9001/api/v1/typical_scenarios/single_point_{UUID}
# 使用UUID
curl -X GET http://localhost:9001/api/v1/typical_scenarios/{UUID}
```

### 删除场景（支持多种标识符）
```bash
# 使用场景名称
curl -X DELETE http://localhost:9001/api/v1/typical_scenarios/新工业园区
# 使用文件夹名称
curl -X DELETE http://localhost:9001/api/v1/typical_scenarios/single_point_{UUID}
```

## CSV文件格式要求

input CSV文件应包含场景的配置数据，格式为：
```csv
39.9200,116.4200,30.0,39.9195,116.4195,1.5
39.9200,116.4200,30.0,39.9205,116.4205,1.5
39.9200,116.4200,30.0,39.9210,116.4210,1.5
...
```

## 技术特点

1. **预测类型分类**: 支持三种预测类型，便于场景管理和使用
2. **文件验证**: 严格验证上传的CSV文件格式
3. **智能命名**: 使用预测类型前缀+UUID的文件夹命名方式
4. **多重查找**: 支持通过场景名称、文件夹名称或UUID进行查找和操作
5. **类型分组**: 列表接口支持按预测类型分组展示场景
6. **类型过滤**: 支持按预测类型快速过滤场景列表
7. **目录管理**: 为每个场景创建独立的目录结构
8. **元数据管理**: 通过JSON文件记录场景的完整信息和类型映射
9. **TIF映射**: 建立场景与tif图像文件的对应关系
10. **错误处理**: 完善的参数验证和错误提示
11. **安全性**: 使用secure_filename防止路径注入攻击

## 部署说明

1. 确保 `storage/typical_scenarios/` 目录存在且有写权限
2. 确保Web服务器支持文件上传
3. 配置合适的文件上传大小限制
4. 运行 `test_typical_scenario_management.py` 验证功能

## 扩展建议

1. 添加更多预测类型支持
2. 支持预测类型的动态配置
3. 增加场景模板导入导出功能
4. 添加场景使用统计和分析
5. 支持场景配置可视化验证
6. 增加场景分享和协作功能