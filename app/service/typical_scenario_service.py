import os
import json
import shutil
import csv
import uuid
from flask import current_app
from typing import Dict, Any, Tuple, Optional, List
from datetime import datetime

# 预测类型映射
PREDICTION_TYPE_MAPPING = {
    "单点预测": "single_point",
    "动态感知": "dynamic_sensing",
    "小尺度预测": "small_scale"
}


def get_available_prediction_types() -> List[str]:
    """
    获取可用的预测类型列表
    
    Returns:
        可用预测类型列表
    """
    return list(PREDICTION_TYPE_MAPPING.keys())


def validate_csv_file(file_path: str) -> Tuple[bool, Optional[str]]:
    """
    验证CSV文件格式
    
    Args:
        file_path: CSV文件路径
    
    Returns:
        (is_valid, error_message)
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as csvfile:
            # 尝试读取CSV文件
            csv_reader = csv.reader(csvfile)
            rows = list(csv_reader)

            if len(rows) == 0:
                return False, "CSV file is empty"

            # 检查是否有数据行（除了可能的标题行）
            if len(rows) < 1:
                return False, "CSV file must contain at least one row of data"

            current_app.logger.info(f"CSV validation passed: {len(rows)} rows found")
            return True, None

    except Exception as e:
        return False, f"Invalid CSV file format: {str(e)}"


def add_typical_scenario_service(scenario_name: str, prediction_type: str, tif_image_name: str,
                                 input_file_path: str) -> Tuple[Optional[Dict], Optional[str]]:
    """
    添加典型场景
    
    Args:
        scenario_name: 典型场景名称
        prediction_type: 预测类型（单点预测、动态感知、小尺度预测）
        tif_image_name: tif图像文件名称
        input_file_path: input CSV文件路径
    
    Returns:
        (result, error_message)
    """
    try:
        # 验证输入参数
        if not scenario_name or not scenario_name.strip():
            return None, "scenario_name is required"

        if not prediction_type or prediction_type not in PREDICTION_TYPE_MAPPING:
            available_types = ', '.join(PREDICTION_TYPE_MAPPING.keys())
            return None, f"Invalid prediction_type. Must be one of: {available_types}"

        if not tif_image_name or not tif_image_name.strip():
            return None, "tif_image_name is required"

        if not input_file_path or not os.path.exists(input_file_path):
            return None, f"input_file_path is invalid or file does not exist: {input_file_path}"

        # 验证文件是否为CSV格式
        if not input_file_path.lower().endswith('.csv'):
            return None, "input_file must be a CSV file"

        # 验证CSV文件格式
        is_valid, validation_error = validate_csv_file(input_file_path)
        if not is_valid:
            return None, f"CSV validation failed: {validation_error}"

        # 生成带类型前缀的文件夹名称
        type_prefix = PREDICTION_TYPE_MAPPING[prediction_type]
        scenario_uuid = str(uuid.uuid4())
        folder_name = f"{type_prefix}_{scenario_uuid}"
        scenario_uuid = folder_name

        # 获取典型场景基础目录
        base_dir = current_app.config.get('TYPICAL_SCENARIO_CSV_DIR', 'storage/typical_scenarios')
        scenario_dir = os.path.join(base_dir, folder_name)

        # 创建场景目录
        os.makedirs(scenario_dir, exist_ok=True)
        current_app.logger.info(f"Created scenario directory: {scenario_dir}")

        # 复制CSV文件到场景目录，确保文件名为input.csv
        input_filename = "input.csv"
        target_input_path = os.path.join(scenario_dir, input_filename)
        shutil.copy2(input_file_path, target_input_path)
        current_app.logger.info(f"Copied CSV input file to: {target_input_path}")

        # 创建元信息文件，记录tif图指令映射
        metadata = {
            "scenario_uuid": scenario_uuid,
            "folder_name": folder_name,
            "scenario_name": scenario_name,
            "prediction_type": prediction_type,
            "prediction_type_code": type_prefix,
            "tif_image_name": tif_image_name,
            "input_file": input_filename,
            "input_file_type": "csv",
            "created_at": datetime.now().isoformat(),
            "description": f"典型场景: {scenario_name} ({prediction_type})",
            "tif_mapping": {
                "source_tif": tif_image_name,
                "scenario_type": "custom_added"
            }
        }

        metadata_file = os.path.join(scenario_dir, "scenario_metadata.json")
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        current_app.logger.info(f"Created metadata file: {metadata_file}")

        result = {
            "scenario_uuid": scenario_uuid,
            "folder_name": folder_name,
            "scenario_name": scenario_name,
            "prediction_type": prediction_type,
            "scenario_directory": scenario_dir,
            "input_file": target_input_path,
            "metadata_file": metadata_file,
            "tif_image_name": tif_image_name,
            "created_at": metadata["created_at"]
        }

        current_app.logger.info(
            f"Successfully added typical scenario: {scenario_name} ({prediction_type}) with UUID: {scenario_uuid}")
        return result, None

    except Exception as e:
        current_app.logger.error(f"Error adding typical scenario '{scenario_name}': {str(e)}")
        return None, f"Failed to add typical scenario: {str(e)}"


def find_scenario_by_name(scenario_name: str, prediction_type: Optional[str] = None) -> Tuple[
    Optional[str], Optional[str]]:
    """
    通过场景名称查找场景文件夹名称
    
    Args:
        scenario_name: 典型场景名称
        prediction_type: 预测类型（可选，用于进一步过滤）
    
    Returns:
        (folder_name, error_message)
    """
    try:
        base_dir = current_app.config.get('TYPICAL_SCENARIO_CSV_DIR', 'storage/typical_scenarios')
        if not os.path.exists(base_dir):
            return None, f"Typical scenario '{scenario_name}' not found"

        for item in os.listdir(base_dir):
            item_path = os.path.join(base_dir, item)
            if os.path.isdir(item_path):
                metadata_file = os.path.join(item_path, "scenario_metadata.json")
                if os.path.exists(metadata_file):
                    try:
                        with open(metadata_file, 'r', encoding='utf-8') as f:
                            metadata = json.load(f)

                        # 匹配场景名称
                        if metadata.get("scenario_name") == scenario_name:
                            # 如果指定了预测类型，还需要匹配类型
                            if prediction_type and metadata.get("prediction_type") != prediction_type:
                                continue
                            return item, None  # item就是文件夹名称(type_prefix_uuid)
                    except Exception as e:
                        current_app.logger.warning(f"Failed to read metadata for {item}: {e}")
                        continue

        type_info = f" with type '{prediction_type}'" if prediction_type else ""
        return None, f"Typical scenario '{scenario_name}'{type_info} not found"

    except Exception as e:
        current_app.logger.error(f"Error finding scenario by name '{scenario_name}': {str(e)}")
        return None, f"Failed to find scenario: {str(e)}"


def get_typical_scenario_info_service(scenario_identifier: str) -> Tuple[Optional[Dict], Optional[str]]:
    """
    获取典型场景信息
    
    Args:
        scenario_identifier: 典型场景名称、文件夹名称(type_prefix_uuid)或UUID
    
    Returns:
        (scenario_info, error_message)
    """
    try:
        base_dir = current_app.config.get('TYPICAL_SCENARIO_CSV_DIR', 'storage/typical_scenarios')

        # 首先尝试作为文件夹名称查找
        scenario_dir = os.path.join(base_dir, scenario_identifier)

        # 如果不存在，尝试通过场景名称查找
        if not os.path.exists(scenario_dir):
            folder_name, error = find_scenario_by_name(scenario_identifier)
            if error:
                return None, error
            scenario_dir = os.path.join(base_dir, folder_name)

        if not os.path.exists(scenario_dir):
            return None, f"Typical scenario '{scenario_identifier}' not found"

        # 读取元信息文件
        metadata_file = os.path.join(scenario_dir, "scenario_metadata.json")
        if os.path.exists(metadata_file):
            with open(metadata_file, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
        else:
            # 如果没有元信息文件，返回基本信息
            metadata = {
                "scenario_name": scenario_identifier,
                "scenario_directory": scenario_dir,
                "note": "Legacy scenario without metadata"
            }

        # 列出目录中的文件
        files = []
        for file in os.listdir(scenario_dir):
            file_path = os.path.join(scenario_dir, file)
            if os.path.isfile(file_path):
                files.append({
                    "name": file,
                    "size": os.path.getsize(file_path),
                    "modified": datetime.fromtimestamp(os.path.getmtime(file_path)).isoformat()
                })

        metadata["files"] = files
        return metadata, None

    except Exception as e:
        current_app.logger.error(f"Error getting typical scenario info '{scenario_identifier}': {str(e)}")
        return None, f"Failed to get scenario info: {str(e)}"


def list_typical_scenarios_by_type_service(prediction_type: str) -> Tuple[Optional[Dict], Optional[str]]:
    """
    根据预测类型列出典型场景
    
    Args:
        prediction_type: 预测类型
        
    Returns:
        (scenarios_info, error_message)
    """
    try:
        # 验证预测类型
        if prediction_type not in PREDICTION_TYPE_MAPPING:
            available_types = ', '.join(PREDICTION_TYPE_MAPPING.keys())
            return None, f"Invalid prediction_type. Must be one of: {available_types}"

        base_dir = current_app.config.get('TYPICAL_SCENARIO_CSV_DIR')
        if not os.path.exists(base_dir):
            return {"scenarios": [], "prediction_type": prediction_type, "total_count": 0}, None

        type_prefix = PREDICTION_TYPE_MAPPING[prediction_type]
        scenarios = []

        for item in os.listdir(base_dir):
            item_path = os.path.join(base_dir, item)
            if os.path.isdir(item_path):
                # 检查是否匹配预测类型前缀
                if item.startswith(f"{type_prefix}_"):
                    scenario_info = {
                        "folder_name": item,
                        "directory": item_path,
                        "type": "directory"
                    }

                    # 尝试读取元信息
                    metadata_file = os.path.join(item_path, "scenario_metadata.json")
                    if os.path.exists(metadata_file):
                        try:
                            with open(metadata_file, 'r', encoding='utf-8') as f:
                                metadata = json.load(f)

                            # 再次验证预测类型是否匹配
                            if metadata.get("prediction_type") == prediction_type:
                                scenario_info.update({
                                    "uuid": metadata.get("scenario_uuid"),
                                    "name": metadata.get("scenario_name"),
                                    "prediction_type": metadata.get("prediction_type"),
                                    "prediction_type_code": metadata.get("prediction_type_code"),
                                    "tif_image_name": metadata.get("tif_image_name"),
                                    "created_at": metadata.get("created_at"),
                                    "description": metadata.get("description"),
                                    "type": "directory_with_metadata"
                                })
                                scenarios.append(scenario_info)
                        except Exception as e:
                            current_app.logger.warning(f"Failed to read metadata for {item}: {e}")
                            # 即使读取元数据失败，但文件夹名称匹配，也添加基本信息
                            scenario_info.update({
                                "prediction_type_code": type_prefix,
                                "name": f"Unknown_{item[:16]}",
                                "prediction_type": prediction_type
                            })
                            scenarios.append(scenario_info)
                    else:
                        # 没有元数据文件但文件夹名称匹配
                        scenario_info.update({
                            "prediction_type_code": type_prefix,
                            "name": f"Unknown_{item[:16]}",
                            "prediction_type": prediction_type
                        })
                        scenarios.append(scenario_info)

        result = {
            "scenarios": scenarios,
            "prediction_type": prediction_type,
            "prediction_type_code": type_prefix,
            "total_count": len(scenarios),
            "base_directory": base_dir
        }

        current_app.logger.info(f"Found {len(scenarios)} scenarios for prediction type '{prediction_type}'")
        return result, None

    except Exception as e:
        current_app.logger.error(f"Error listing scenarios by type '{prediction_type}': {str(e)}")
        return None, f"Failed to list scenarios by type: {str(e)}"


def list_all_typical_scenarios_service() -> Tuple[Optional[Dict], Optional[str]]:
    """
    列出所有典型场景
    
    Returns:
        (scenarios_info, error_message)
    """
    try:
        base_dir = current_app.config.get('TYPICAL_SCENARIO_CSV_DIR')
        if not os.path.exists(base_dir):
            return {"scenarios": []}, None

        scenarios = []

        for item in os.listdir(base_dir):
            item_path = os.path.join(base_dir, item)
            if os.path.isdir(item_path):
                # 这是一个场景目录（type_prefix_uuid命名）
                scenario_info = {
                    "folder_name": item,
                    "directory": item_path,
                    "type": "directory"
                }

                # 尝试读取元信息
                metadata_file = os.path.join(item_path, "scenario_metadata.json")
                if os.path.exists(metadata_file):
                    try:
                        with open(metadata_file, 'r', encoding='utf-8') as f:
                            metadata = json.load(f)
                        scenario_info.update({
                            "uuid": metadata.get("scenario_uuid"),
                            "name": metadata.get("scenario_name"),
                            "prediction_type": metadata.get("prediction_type"),
                            "prediction_type_code": metadata.get("prediction_type_code"),
                            "tif_image_name": metadata.get("tif_image_name"),
                            "created_at": metadata.get("created_at"),
                            "description": metadata.get("description"),
                            "type": "directory_with_metadata"
                        })
                    except Exception as e:
                        current_app.logger.warning(f"Failed to read metadata for {item}: {e}")
                        # 尝试从文件夹名称解析类型
                        if '_' in item:
                            type_prefix = item.split('_')[0]
                            scenario_info["prediction_type_code"] = type_prefix
                            scenario_info["name"] = f"Unknown_{item[:16]}"
                        else:
                            scenario_info["name"] = f"Unknown_{item[:8]}"

                scenarios.append(scenario_info)
            elif item.endswith('.csv'):
                # 这是一个CSV文件（旧的格式）
                scenarios.append({
                    "name": item.replace('.csv', ''),
                    "file": item_path,
                    "type": "csv_file"
                })

        # 按预测类型分组
        scenarios_by_type = {}
        for scenario in scenarios:
            pred_type = scenario.get("prediction_type", "未知类型")
            if pred_type not in scenarios_by_type:
                scenarios_by_type[pred_type] = []
            scenarios_by_type[pred_type].append(scenario)

        result = {
            "scenarios": scenarios,
            "scenarios_by_type": scenarios_by_type,
            "total_count": len(scenarios),
            "base_directory": base_dir
        }

        return result, None

    except Exception as e:
        current_app.logger.error(f"Error listing typical scenarios: {str(e)}")
        return None, f"Failed to list scenarios: {str(e)}"


def delete_typical_scenario_service(scenario_identifier: str) -> Tuple[Optional[Dict], Optional[str]]:
    """
    删除典型场景
    
    Args:
        scenario_identifier: 典型场景名称、文件夹名称(type_prefix_uuid)或UUID
    
    Returns:
        (result, error_message)
    """
    try:
        base_dir = current_app.config.get('TYPICAL_SCENARIO_CSV_DIR', 'storage/typical_scenarios')

        # 首先尝试作为文件夹名称查找
        scenario_dir = os.path.join(base_dir, scenario_identifier)
        folder_name = scenario_identifier
        scenario_name = scenario_identifier
        scenario_uuid = scenario_identifier
        prediction_type = "未知"

        # 如果不存在，尝试通过场景名称查找
        if not os.path.exists(scenario_dir):
            found_folder, error = find_scenario_by_name(scenario_identifier)
            if error:
                return None, error
            folder_name = found_folder
            scenario_name = scenario_identifier
            scenario_dir = os.path.join(base_dir, folder_name)

        # 尝试获取详细信息
        metadata_file = os.path.join(scenario_dir, "scenario_metadata.json")
        if os.path.exists(metadata_file):
            try:
                with open(metadata_file, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
                scenario_name = metadata.get("scenario_name", scenario_identifier)
                scenario_uuid = metadata.get("scenario_uuid", scenario_identifier)
                prediction_type = metadata.get("prediction_type", "未知")
            except:
                pass

        if not os.path.exists(scenario_dir):
            return None, f"Typical scenario '{scenario_identifier}' not found"

        # 删除整个场景目录
        shutil.rmtree(scenario_dir)

        result = {
            "scenario_uuid": scenario_uuid,
            "folder_name": folder_name,
            "scenario_name": scenario_name,
            "prediction_type": prediction_type,
            "deleted_directory": scenario_dir,
            "deleted_at": datetime.now().isoformat()
        }

        current_app.logger.info(
            f"Successfully deleted typical scenario: {scenario_name} ({prediction_type}) - {folder_name}")
        return result, None

    except Exception as e:
        current_app.logger.error(f"Error deleting typical scenario '{scenario_identifier}': {str(e)}")
        return None, f"Failed to delete typical scenario: {str(e)}"
