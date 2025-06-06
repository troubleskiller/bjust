# 场景选择功能实现总结

## 功能概述

已成功为预测任务创建接口`/online_deduction/tasks`添加了场景选择功能，支持三种场景类型：

1. **自主选点** (`manual_selection`) - 用户通过场景描述字符串自主选择
2. **典型场景** (`typical_scenario`) - 通过场景名称选择预设的典型场景配置
3. **自定义上传** (`custom_upload`) - 用户上传自定义场景描述

## 可用典型场景

系统提供以下6种典型场景：
- **城市商业区** - 高层建筑密集的商业中心区域
- **室内办公室** - 办公楼内部WiFi覆盖场景  
- **工业园区** - 工厂厂区的无线网络部署
- **居民社区** - 住宅小区的信号覆盖
- **高速公路** - 高速公路沿线的基站覆盖
- **地铁隧道** - 地下轨道交通的信号分布

## 修改文件清单

### 1. 路由层修改
- **文件**: `app/route/online_deduction_route.py`
- **修改**: 
  - 增加 `scenario_type` 必填参数
  - 典型场景使用 `scenario_name` 而非 `csv_file_name`
  - 新增 `/typical_scenarios` 接口获取可用场景列表
  - 更新API文档，添加场景类型相关参数说明

### 2. 服务层修改  
- **文件**: `app/service/online_deduction_service.py`
- **新增功能**:
  - `TYPICAL_SCENARIO_MAPPING` - 场景名称到CSV文件的映射
  - `get_available_typical_scenarios()` - 获取可用典型场景列表
  - `load_typical_scenario_csv()` - 通过场景名称加载典型场景配置
- **修改内容**:
  - 场景类型验证
  - 根据场景类型处理不同的输入配置
  - 支持通过场景名称读取对应CSV文件

### 3. 配置文件修改
- **文件**: `config.py`  
- **新增**: `TYPICAL_SCENARIO_CSV_DIR` 配置项，指定典型场景CSV文件存储目录

### 4. 创建目录结构和示例文件
- **目录**: `storage/typical_scenarios/`
- **CSV文件**:
  - `urban_commercial_scenario.csv` - 城市商业区场景
  - `indoor_office_scenario.csv` - 室内办公室场景
  - `industrial_park_scenario.csv` - 工业园区场景
  - `residential_community_scenario.csv` - 居民社区场景
  - `highway_scenario.csv` - 高速公路场景
  - `subway_tunnel_scenario.csv` - 地铁隧道场景
- **文档**: `README.md` - 使用说明文档

### 5. 测试脚本
- **文件**: `test_scenario_api.py`
- **功能**: 测试三种场景类型的API调用和获取典型场景列表

## API使用示例

### 获取典型场景列表
```http
GET /api/v1/online_deduction/typical_scenarios
```
返回：
```json
{
  "code": "200",
  "message": "success", 
  "data": ["城市商业区", "室内办公室", "工业园区", "居民社区", "高速公路", "地铁隧道"]
}
```

### 自主选点场景
```json
{
  "model_uuid": "uuid-model-001",
  "prediction_mode": "link",
  "scenario_type": "manual_selection", 
  "point_config": {
    "scenario_description": "北京CBD商业区5G信号覆盖预测",
    "tx_pos_list": [...],
    "rx_pos_list": [...]
  },
  "param_config": {...}
}
```

### 典型场景
```json
{
  "model_uuid": "uuid-model-002",
  "prediction_mode": "point",
  "scenario_type": "typical_scenario",
  "point_config": {
    "scenario_name": "城市商业区"
  },
  "param_config": {...}
}
```

### 自定义上传场景
```json
{
  "model_uuid": "uuid-model-003", 
  "prediction_mode": "situation",
  "scenario_type": "custom_upload",
  "point_config": {
    "scenario_description": "用户自定义的工厂厂区WiFi覆盖场景",
    "tx_pos_list": [...],
    "area_bounds": {...},
    "resolution_m": 1.0
  },  
  "param_config": {...}
}
```

## 技术特点

1. **向后兼容**: 保持原有API结构，只新增必要参数
2. **灵活扩展**: 易于添加新的场景类型和典型场景
3. **错误处理**: 完善的参数验证和错误提示
4. **文档完善**: 包含API文档和使用示例
5. **测试覆盖**: 提供完整的测试脚本
6. **场景管理**: 通过映射表管理场景名称与文件的对应关系

## 部署说明

1. 确保 `storage/typical_scenarios/` 目录存在
2. 确保所有典型场景CSV文件已创建
3. 运行 `test_scenario_api.py` 验证功能正常

## 扩展建议

1. 可考虑增加场景预览功能
2. 支持批量上传典型场景文件
3. 增加场景配置可视化展示
4. 添加场景模板管理功能
5. 支持动态添加新的典型场景而无需重启服务 