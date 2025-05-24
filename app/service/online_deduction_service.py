from app.model.model_info import Model
from app import db
import uuid
import json
import csv
import os
from typing import Dict, Any, List, Tuple, Optional
from datetime import datetime
from flask import current_app

# This mapping might need to be more sophisticated or stored elsewhere (e.g., in the database)
# if a model can belong to multiple task types or if task_types are more dynamic.
TASK_TYPE_TO_MODEL_TYPE_MAPPING = {
    "single_point_prediction": "large_scale",
    "situation_prediction": "situation_awareness",
    "small_scale_prediction": "small_scale",
}

def get_online_models_by_task_type_service(task_type: str) -> Tuple[List[Dict], Optional[str]]:
    """
    根据任务类型获取可用的在线推演模型列表
    
    Args:
        task_type: 任务类型 ("single_point_prediction", "situation_prediction", "small_scale_prediction")
    
    Returns:
        (models_list, error_message)
    """
    try:
        # 验证任务类型
        valid_task_types = ["single_point_prediction", "situation_prediction", "small_scale_prediction"]
        if task_type not in valid_task_types:
            return [], f"Invalid task_type. Must be one of: {', '.join(valid_task_types)}"

        # TODO: 这里应该从数据库查询符合条件的模型
        # 暂时返回模拟数据
        mock_models = [
            {
                "model_uuid": "uuid-model-001",
                "model_name": "RayTracer-Pro",
                "model_description": "基于射线追踪的精确信道模型。",
                "model_img": "/storage/models/raytracer_pro_thumb.jpg",
                "model_doc_url": "/models/uuid-model-001/documentation"
            },
            {
                "model_uuid": "uuid-model-002",
                "model_name": "StatisticalModel-A",
                "model_description": "基于统计的信道预测模型。",
                "model_img": "/storage/models/statistical_a_thumb.jpg",
                "model_doc_url": "/models/uuid-model-002/documentation"
            }
        ]
        
        return mock_models, None
        
    except Exception as e:
        current_app.logger.error(f"Error in get_online_models_by_task_type_service: {str(e)}")
        return [], f"Database error: {str(e)}"


def generate_tx_rx_pairs_csv(point_config: Dict[str, Any], task_uuid: str) -> Tuple[Optional[str], Optional[str]]:
    """
    生成发射机-接收机配对的CSV文件
    
    Args:
        point_config: 点位配置信息
        task_uuid: 任务UUID
    
    Returns:
        (csv_file_path, error_message)
    """
    try:
        # 获取发射机和接收机位置列表
        tx_pos_list = point_config.get('tx_pos_list', [])
        rx_pos_list = point_config.get('rx_pos_list', [])
        
        if not tx_pos_list or not rx_pos_list:
            return None, "tx_pos_list and rx_pos_list are required"
        
        # 创建CSV文件目录
        csv_dir = current_app.config.get('TASK_CSV_DIR', 'storage/tasks/csv')
        os.makedirs(csv_dir, exist_ok=True)
        
        # 生成CSV文件路径
        csv_filename = f"{task_uuid}_tx_rx_pairs.csv"
        csv_file_path = os.path.join(csv_dir, csv_filename)
        
        # 写入CSV文件
        with open(csv_file_path, 'w', newline='', encoding='utf-8') as csvfile:
            csv_writer = csv.writer(csvfile)
            
            # 写入标题行
            csv_writer.writerow([
                '接收机纬度', '接收机经度', '接收机高度', 
                '发射机纬度', '发射机经度', '发射机高度'
            ])
            
            # 生成所有发射机-接收机配对
            for tx_pos in tx_pos_list:
                for rx_pos in rx_pos_list:
                    row = [
                        rx_pos.get('lat', 0),      # 接收机纬度
                        rx_pos.get('lon', 0),      # 接收机经度  
                        rx_pos.get('height', 0),   # 接收机高度
                        tx_pos.get('lat', 0),      # 发射机纬度
                        tx_pos.get('lon', 0),      # 发射机经度
                        tx_pos.get('height', 0)    # 发射机高度
                    ]
                    csv_writer.writerow(row)
        
        current_app.logger.info(f"Generated CSV file: {csv_file_path}")
        return csv_file_path, None
        
    except Exception as e:
        current_app.logger.error(f"Error generating CSV file: {str(e)}")
        return None, f"Failed to generate CSV file: {str(e)}"


def create_prediction_task_service(task_data: Dict[str, Any]) -> Tuple[Optional[Dict], Optional[str]]:
    """
    创建预测任务
    
    Args:
        task_data: 任务数据
    
    Returns:
        (result, error_message)
    """
    try:
        # 验证必要字段
        required_fields = ['model_uuid', 'prediction_mode', 'point_config', 'param_config']
        for field in required_fields:
            if field not in task_data:
                return None, f"Missing required field: {field}"

        # 验证预测模式
        valid_modes = ["point", "link", "situation", "small_scale"]
        prediction_mode = task_data['prediction_mode']
        if prediction_mode not in valid_modes:
            return None, f"Invalid prediction_mode. Must be one of: {', '.join(valid_modes)}"

        # 验证point_config
        point_config = task_data['point_config']
        if not isinstance(point_config, dict):
            return None, "point_config must be a dictionary"

        # 根据预测模式验证配置
        if prediction_mode in ["point", "link"]:
            if 'tx_pos_list' not in point_config:
                return None, "tx_pos_list is required for point and link modes"
            if 'rx_pos_list' not in point_config:
                return None, "rx_pos_list is required for point and link modes"
        elif prediction_mode == "situation":
            if 'tx_pos_list' not in point_config:
                return None, "tx_pos_list is required for situation mode"
        elif prediction_mode == "small_scale":
            if 'tx_pos_list' not in point_config:
                return None, "tx_pos_list is required for small_scale mode"
            if 'rx_pos_list' not in point_config:
                return None, "rx_pos_list is required for small_scale mode"
            # 验证调制参数
            param_config = task_data['param_config']
            if 'modulation_mode' not in param_config or 'modulation_order' not in param_config:
                return None, "modulation_mode and modulation_order are required for small_scale mode"

        # 生成任务UUID
        task_uuid = f"pred-task-{str(uuid.uuid4())}"
        
        # 为需要发射机-接收机配对的模式生成CSV文件
        csv_file_path = None
        if prediction_mode in ["point", "link", "small_scale"]:
            csv_file_path, csv_error = generate_tx_rx_pairs_csv(point_config, task_uuid)
            if csv_error:
                current_app.logger.warning(f"Failed to generate CSV for task {task_uuid}: {csv_error}")
                # 不中断任务创建，只记录警告
        
        # TODO: 这里应该将任务保存到数据库并启动后台计算任务
        # 暂时直接返回成功结果
        
        result = {
            "task_uuid": task_uuid,
            "prediction_mode": prediction_mode,
            "csv_file_path": csv_file_path  # 可选：返回CSV文件路径
        }
        
        current_app.logger.info(f"Created prediction task {task_uuid} with mode {prediction_mode}")
        if csv_file_path:
            current_app.logger.info(f"Generated CSV file: {csv_file_path}")
        
        return result, None
        
    except Exception as e:
        current_app.logger.error(f"Error in create_prediction_task_service: {str(e)}")
        return None, f"Service error: {str(e)}"


def get_prediction_task_result_service(task_uuid: str, next_index: Optional[int] = None, 
                                     batch_size: Optional[int] = None, 
                                     batch_mode: bool = True) -> Tuple[Optional[Dict], Optional[str]]:
    """
    获取预测任务结果
    
    Args:
        task_uuid: 任务UUID
        next_index: 下一个要获取的点的序号 (用于增量获取)
        batch_size: 批次大小
        batch_mode: 是否为批次模式 (True for /results, False for /result)
    
    Returns:
        (result, error_message)
    """
    try:
        # TODO: 这里应该从数据库查询任务信息和结果
        # 暂时返回模拟数据
        
        # 模拟检查任务是否存在
        if not task_uuid.startswith("pred-task-"):
            return None, "Task not found"
        
        if batch_mode:
            # 返回增量结果 (用于point和link模式)
            mock_result = {
                "task_uuid": task_uuid,
                "status": "IN_PROGRESS",
                "prediction_mode": "link",
                "total_samples": 100,
                "completed_samples": 50,
                "results": [
                    {
                        "sample_index": 0,
                        "pos": {"lat": 39.916, "lon": 116.405, "height": 1.5},
                        "distance_from_start_m": 0.0,
                        "path_loss_db": 95.5
                    },
                    {
                        "sample_index": 1,
                        "pos": {"lat": 39.917, "lon": 116.406, "height": 1.5},
                        "distance_from_start_m": 100.0,
                        "path_loss_db": 98.2
                    }
                ]
            }
        else:
            # 返回完整结果 (用于situation和small_scale模式)
            mock_result = {
                "task_uuid": task_uuid,
                "status": "COMPLETED",
                "prediction_mode": "situation",
                "result": {
                    "heatmap_data_type": "grid",
                    "grid_origin": {"lat": 39.900, "lon": 116.390},
                    "cell_size_deg": {"lat_delta": 0.0001, "lon_delta": 0.0001},
                    "rows": 300,
                    "cols": 300,
                    "values": [[100.5, 101.2], [102.1, 103.0]],  # 简化的示例数据
                    "value_unit": "dB"
                }
            }
        
        return mock_result, None
        
    except Exception as e:
        current_app.logger.error(f"Error in get_prediction_task_result_service: {str(e)}")
        return None, f"Service error: {str(e)}" 