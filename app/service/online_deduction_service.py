import uuid
import json
import csv
import os
import shutil
import shlex
from typing import Dict, Any, List, Tuple, Optional
from datetime import datetime
from flask import current_app
from enum import Enum
from app.utils.process_manager import ProcessManager

# 任务状态枚举
class OnlineDeductionStatus(Enum):
    NOT_STARTED = "NOT_STARTED"
    IN_PROGRESS = "IN_PROGRESS" 
    COMPLETED = "COMPLETED"
    ABORTED = "ABORTED"

# 内存中存储任务状态（简化实现，生产环境建议使用数据库）
TASK_STATUS_STORE = {}

# This mapping might need to be more sophisticated or stored elsewhere (e.g., in the database)
# if a model can belong to multiple task types or if task_types are more dynamic.
TASK_TYPE_TO_MODEL_TYPE_MAPPING = {
    "single_point_prediction": "large_scale",
    "situation_prediction": "situation_awareness",
    "small_scale_prediction": "small_scale",
}

# 典型场景名称到CSV文件的映射
TYPICAL_SCENARIO_MAPPING = {
    "城市商业区": "urban_commercial_scenario.csv",
    "室内办公室": "indoor_office_scenario.csv",
    "工业园区": "industrial_park_scenario.csv",
    "居民社区": "residential_community_scenario.csv",
    "高速公路": "highway_scenario.csv",
    "地铁隧道": "subway_tunnel_scenario.csv"
}

# 创建进程管理器实例
_process_manager = ProcessManager()

def _get_app():
    """
    获取应用实例（延迟导入避免循环引用）
    """
    # 延迟导入避免循环引用
    from app import create_app
    return create_app()

def _on_process_complete(process_id: str, return_code: int):
    """
    进程结束时的回调函数
    """
    # 使用current_app而不是创建新的app实例
    try:
        # 更新任务状态
        if process_id in TASK_STATUS_STORE:
            task_info = TASK_STATUS_STORE[process_id]
            if return_code == 0:
                task_info['status'] = OnlineDeductionStatus.COMPLETED.value
                task_info['message'] = '任务完成'
            else:
                task_info['status'] = OnlineDeductionStatus.ABORTED.value
                task_info['message'] = f'任务异常结束，返回码: {return_code}'
            task_info['end_time'] = datetime.now().isoformat()
            
            # 尝试读取输出结果
            try:
                # 从任务文件夹中读取output.csv（根据main.py的输出文件名）
                task_folder_path = task_info.get('task_folder_path')
                if task_folder_path:
                    output_csv_path = os.path.join(task_folder_path, 'output.csv')
                    if os.path.exists(output_csv_path):
                        with open(output_csv_path, 'r', encoding='utf-8') as f:
                            task_info['result_csv_content'] = f.read()
                    else:
                        current_app.logger.warning(f"Output CSV file not found: {output_csv_path}")
                        task_info['result_csv_content'] = ""
                else:
                    current_app.logger.warning(f"Task folder path not found for task {process_id}")
                    task_info['result_csv_content'] = ""
            except Exception as e:
                if current_app:
                    current_app.logger.error(f"读取任务结果失败: {str(e)}")
                task_info['result_csv_content'] = ""
            
            TASK_STATUS_STORE[process_id] = task_info
            
    except Exception as e:
        if current_app:
            current_app.logger.error(f"更新在线推演任务状态时发生错误: {str(e)}")
        else:
            print(f"更新在线推演任务状态时发生错误: {str(e)}")

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


def get_available_typical_scenarios() -> List[str]:
    """
    获取可用的典型场景列表
    
    Returns:
        可用场景名称列表
    """
    return list(TYPICAL_SCENARIO_MAPPING.keys())

def load_typical_scenario_by_uuid(scenario_uuid: str) -> Tuple[Optional[Dict], Optional[str]]:
    """
    通过典型场景UUID加载场景配置
    
    Args:
        scenario_uuid: 典型场景UUID
    
    Returns:
        (point_config, error_message)
    """
    try:
        # 获取典型场景基础目录
        base_dir = current_app.config.get('TYPICAL_SCENARIO_CSV_DIR', 'storage/typical_scenarios')
        if not os.path.exists(base_dir):
            return None, f"Typical scenarios directory not found"
        
        # 查找匹配的场景目录
        scenario_dir = None
        scenario_info = None
        
        for item in os.listdir(base_dir):
            item_path = os.path.join(base_dir, item)
            if os.path.isdir(item_path):
                # 检查元数据文件
                metadata_file = os.path.join(item_path, "scenario_metadata.json")
                if os.path.exists(metadata_file):
                    try:
                        with open(metadata_file, 'r', encoding='utf-8') as f:
                            metadata = json.load(f)
                        
                        # 检查UUID是否匹配
                        if metadata.get("scenario_uuid") == scenario_uuid:
                            scenario_dir = item_path
                            scenario_info = metadata
                            break
                    except Exception as e:
                        current_app.logger.warning(f"Failed to read metadata for {item}: {e}")
                        continue
        
        if not scenario_dir:
            return None, f"Typical scenario with UUID '{scenario_uuid}' not found"
        
        # 读取input.csv文件
        input_csv_path = os.path.join(scenario_dir, "input.csv")
        if not os.path.exists(input_csv_path):
            return None, f"Input CSV file not found for scenario '{scenario_uuid}'"
        
        tx_pos_list = []
        rx_pos_list = []
        
        # 读取CSV文件
        with open(input_csv_path, 'r', encoding='utf-8') as csvfile:
            csv_reader = csv.reader(csvfile)
            for row in csv_reader:
                # 跳过空行
                if not row or len(row) < 6:
                    continue
                
                try:
                    # 假设CSV格式为：tx_lat, tx_lon, tx_height, rx_lat, rx_lon, rx_height
                    # 如果第一行是标题行（包含非数字），跳过
                    tx_lat = float(row[0])
                    tx_lon = float(row[1]) 
                    tx_height = float(row[2])
                    rx_lat = float(row[3])
                    rx_lon = float(row[4])
                    rx_height = float(row[5])
                    
                    tx_pos = {
                        'lat': tx_lat,
                        'lon': tx_lon,
                        'height': tx_height
                    }
                    rx_pos = {
                        'lat': rx_lat,
                        'lon': rx_lon,
                        'height': rx_height
                    }
                    
                    # 避免重复添加相同的发射机位置
                    if tx_pos not in tx_pos_list:
                        tx_pos_list.append(tx_pos)
                    # 避免重复添加相同的接收机位置  
                    if rx_pos not in rx_pos_list:
                        rx_pos_list.append(rx_pos)
                        
                except (ValueError, IndexError) as e:
                    # 可能是标题行或无效数据，跳过
                    current_app.logger.debug(f"Skipping row in CSV: {row}, error: {e}")
                    continue
        
        if not tx_pos_list or not rx_pos_list:
            return None, f"No valid position data found in scenario '{scenario_uuid}'"
        
        # 读取CSV文件内容作为字符串
        csv_content = ""
        try:
            with open(input_csv_path, 'r', encoding='utf-8') as csvfile:
                csv_content = csvfile.read()
        except Exception as e:
            current_app.logger.warning(f"Failed to read CSV content as string for scenario '{scenario_uuid}': {e}")
            csv_content = ""
        
        point_config = {
            'tx_pos_list': tx_pos_list,
            'rx_pos_list': rx_pos_list,
            'scenario_source': f"typical_scenario:{scenario_uuid}",
            'scenario_info': scenario_info,
            'csv_content': csv_content  # 添加CSV文件的字符串内容
        }
        
        current_app.logger.info(f"Loaded typical scenario '{scenario_uuid}': {len(tx_pos_list)} TX, {len(rx_pos_list)} RX")
        return point_config, None
        
    except Exception as e:
        current_app.logger.error(f"Error loading typical scenario '{scenario_uuid}': {str(e)}")
        return None, f"Failed to load typical scenario: {str(e)}"


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
        required_fields = ['model_uuid', 'prediction_mode', 'scenario_type', 'point_config', 'param_config']
        for field in required_fields:
            if field not in task_data:
                return None, f"Missing required field: {field}"

        # 验证预测模式
        valid_modes = ["point", "link", "situation", "small_scale"]
        prediction_mode = task_data['prediction_mode']
        if prediction_mode not in valid_modes:
            return None, f"Invalid prediction_mode. Must be one of: {', '.join(valid_modes)}"

        # 验证场景类型
        valid_scenario_types = ["manual_selection", "typical_scenario", "custom_upload"]
        scenario_type = task_data['scenario_type']
        if scenario_type not in valid_scenario_types:
            return None, f"Invalid scenario_type. Must be one of: {', '.join(valid_scenario_types)}"

        # 获取原始point_config
        original_point_config = task_data['point_config']
        if not isinstance(original_point_config, dict):
            return None, "point_config must be a dictionary"

        # 根据场景类型处理point_config
        point_config = {}
        
        if scenario_type == "typical_scenario":
            # 典型场景：通过场景UUID加载配置
            scenario_uuid = original_point_config.get('scenario_uuid')
            if not scenario_uuid:
                return None, "scenario_uuid is required for typical_scenario mode"
            
            loaded_config, load_error = load_typical_scenario_by_uuid(scenario_uuid)
            if load_error:
                return None, load_error
            
            point_config = loaded_config
            
        elif scenario_type in ["manual_selection", "custom_upload"]:
            # 自主选点和自定义上传：使用scenario_description
            scenario_description = original_point_config.get('scenario_description')
            if not scenario_description:
                return None, f"scenario_description is required for {scenario_type} mode"
            
            # 保留原有的点位配置（如果有的话）
            point_config = {
                'scenario_description': scenario_description,
                'scenario_source': scenario_type
            }
            
            # 复制其他配置
            for key in ['tx_pos_list', 'rx_pos_list', 'area_bounds', 'resolution_m']:
                if key in original_point_config:
                    point_config[key] = original_point_config[key]

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

        # 生成任务UUID和文件夹名称
        task_uuid = str(uuid.uuid4())
        task_folder_name = f"ONLINE-DEDUCTION-{task_uuid}"
        
        # 创建任务文件夹
        task_folder_path = os.path.join(
            current_app.config.get('TASK_OUTPUT_DIR', 'storage/tasks'),
            task_folder_name
        )
        os.makedirs(task_folder_path, exist_ok=True)
        
        # 生成input.csv文件
        input_csv_path = os.path.join(task_folder_path, 'input.csv')
        csv_generation_error = None
        
        if prediction_mode in ["point", "link", "small_scale"]:
            # 生成发射机-接收机配对的CSV文件
            csv_generation_error = _generate_tx_rx_pairs_csv_to_path(point_config, input_csv_path, task_data.get('param_config'))
        elif scenario_type == "typical_scenario" and 'csv_content' in point_config:
            # 直接使用典型场景的CSV内容
            try:
                with open(input_csv_path, 'w', encoding='utf-8') as f:
                    f.write(point_config['csv_content'])
            except Exception as e:
                csv_generation_error = f"Failed to write typical scenario CSV: {str(e)}"
        
        if csv_generation_error:
            # 清理已创建的文件夹
            try:
                shutil.rmtree(task_folder_path)
            except:
                pass
            return None, csv_generation_error
        
        # 创建任务元信息文件
        task_metadata = {
            "task_uuid": task_uuid,
            "task_folder_name": task_folder_name,
            "prediction_mode": prediction_mode,
            "scenario_type": scenario_type,
            "model_uuid": task_data.get('model_uuid'),
            "param_config": task_data.get('param_config', {}),
            "created_at": datetime.now().isoformat(),
            "status": OnlineDeductionStatus.NOT_STARTED.value,
            "input_file": "input.csv",
            "task_folder_path": task_folder_path
        }
        
        # 如果是典型场景，添加场景信息
        if scenario_type == "typical_scenario" and 'scenario_info' in point_config:
            task_metadata["scenario_info"] = point_config['scenario_info']
        
        # 保存元信息文件
        metadata_file_path = os.path.join(task_folder_path, 'task_metadata.json')
        with open(metadata_file_path, 'w', encoding='utf-8') as f:
            json.dump(task_metadata, f, indent=2, ensure_ascii=False)
        
        # 初始化任务状态
        task_info = {
            'task_uuid': task_uuid,
            'task_folder_name': task_folder_name,
            'task_folder_path': task_folder_path,
            'prediction_mode': prediction_mode,
            'scenario_type': scenario_type,
            'status': OnlineDeductionStatus.NOT_STARTED.value,
            'message': '任务已创建',
            'created_at': datetime.now().isoformat(),
            'start_time': None,
            'end_time': None,
            'result_csv_content': None,
            'input_csv_path': input_csv_path,
            'metadata_file_path': metadata_file_path,
            'model_uuid': task_data.get('model_uuid')
        }
        
        # 如果是典型场景，保存相关信息
        if scenario_type == "typical_scenario" and 'csv_content' in point_config:
            task_info["scenario_csv_content"] = point_config['csv_content']
            task_info["scenario_info"] = point_config.get('scenario_info', {})
        
        # 存储任务状态
        TASK_STATUS_STORE[task_uuid] = task_info
        
        try:
            # 实际启动模型运行
            run_result = _run_prediction_model(task_uuid, task_data, point_config, task_folder_path)
            task_info.update(run_result)
            TASK_STATUS_STORE[task_uuid] = task_info
        except Exception as e:
            current_app.logger.error(f"启动预测任务失败: {str(e)}")
            task_info['status'] = OnlineDeductionStatus.ABORTED.value
            task_info['message'] = f"启动失败: {str(e)}"
            TASK_STATUS_STORE[task_uuid] = task_info
        
        # 构建返回结果
        result = {
            "task_uuid": task_uuid,
            "task_folder_name": task_folder_name,
            "task_folder_path": task_folder_path,
            "prediction_mode": prediction_mode,
            "scenario_type": scenario_type,
            "status": task_info['status'],
            "message": task_info['message']
        }
        
        # 如果是典型场景，返回CSV内容
        if scenario_type == "typical_scenario" and 'csv_content' in point_config:
            result["scenario_csv_content"] = point_config['csv_content']
            result["scenario_info"] = point_config.get('scenario_info', {})
        
        current_app.logger.info(f"Created prediction task {task_uuid} in folder {task_folder_name}")
        
        return result, None
        
    except Exception as e:
        current_app.logger.error(f"Error in create_prediction_task_service: {str(e)}")
        return None, f"Service error: {str(e)}"


def _generate_tx_rx_pairs_csv_to_path(point_config: Dict[str, Any], csv_file_path: str, param_config: Dict[str, Any] = None) -> Optional[str]:
    """
    生成发射机-接收机配对的CSV文件到指定路径
    
    Args:
        point_config: 点位配置信息
        csv_file_path: CSV文件保存路径
        param_config: 参数配置（包含频率等信息）
    
    Returns:
        error_message (None if success)
    """
    try:
        # 获取发射机和接收机位置列表
        tx_pos_list = point_config.get('tx_pos_list', [])
        rx_pos_list = point_config.get('rx_pos_list', [])
        
        if not tx_pos_list or not rx_pos_list:
            return "tx_pos_list and rx_pos_list are required"
        
        # 获取频率参数（默认为5.9GHz对应的数值）
        frequency = 5900  # 默认5.9GHz，单位MHz
        if param_config and 'frequency_band' in param_config:
            freq_str = param_config['frequency_band']
            # 简单解析频率字符串，如"5.9GHz"
            if 'GHz' in freq_str:
                freq_val = float(freq_str.replace('GHz', '').strip())
                frequency = int(freq_val * 1000)  # 转换为MHz
        
        # 写入CSV文件
        with open(csv_file_path, 'w', newline='', encoding='utf-8') as csvfile:
            csv_writer = csv.writer(csvfile)
            # 生成所有发射机-接收机配对
            for tx_pos in tx_pos_list:
                for rx_pos in rx_pos_list:
                    # 按照main.py期望的格式：tx_lat, tx_lon, tx_height, rx_lat, rx_lon, rx_height, frequency
                    row = [
                        tx_pos.get('lat', 0),      # 发射机纬度
                        tx_pos.get('lon', 0),      # 发射机经度
                        tx_pos.get('height', 0),   # 发射机高度
                        rx_pos.get('lat', 0),      # 接收机纬度
                        rx_pos.get('lon', 0),      # 接收机经度  
                        rx_pos.get('height', 0),   # 接收机高度
                        frequency                   # 频率（MHz）
                    ]
                    csv_writer.writerow(row)
        
        current_app.logger.info(f"Generated CSV file: {csv_file_path}")
        return None
        
    except Exception as e:
        current_app.logger.error(f"Error generating CSV file: {str(e)}")
        return f"Failed to generate CSV file: {str(e)}"


def _run_prediction_model(task_uuid: str, task_data: Dict[str, Any], point_config: Dict[str, Any], task_folder_path: str) -> Dict[str, Any]:
    """
    实际运行预测模型
    """
    try:
        model_uuid = task_data.get('model_uuid')
        if not model_uuid:
            raise ValueError("缺少模型UUID")
        
        # 输入CSV文件路径
        input_csv_path = os.path.join(task_folder_path, 'input.csv')
        
        # 输出CSV文件路径（与main.py的输出文件名一致）
        output_csv_path = os.path.join(task_folder_path, 'output.csv')
        
        # 构建运行环境
        work_dir = os.path.join(
            current_app.config.get('STORAGE_FOLDER'),
            current_app.config.get('MODEL_FOLDER'),
            model_uuid,
            current_app.config.get('MODEL_CODE_FOLDER')
        )
        
        # 环境变量
        env = os.environ.copy()
        env_path = os.path.join(
            current_app.config.get('STORAGE_FOLDER'),
            current_app.config.get('MODEL_FOLDER'),
            model_uuid,
            current_app.config.get('MODEL_PYTHON_ENV_FOLDER'),
            'Library',
            'bin'
        )
        env["PATH"] = env_path + os.pathsep + env["PATH"]
        
        # Python解释器路径
        python_exe = os.path.join(
            current_app.config.get('STORAGE_FOLDER'),
            current_app.config.get('MODEL_FOLDER'),
            model_uuid,
            current_app.config.get('MODEL_PYTHON_ENV_FOLDER'),
            'python.exe'
        )
        
        # 脚本路径
        script_path = os.path.join(
            current_app.config.get('STORAGE_FOLDER'),
            current_app.config.get('MODEL_FOLDER'),
            model_uuid,
            current_app.config.get('MODEL_CODE_FOLDER'),
            'main.py'
        )
        
        # 构建命令
        cmd = [python_exe, script_path]
        
        # 添加输入目录路径（任务文件夹）
        cmd.append(task_folder_path)
        
        # 添加输出目录路径（同样是任务文件夹）
        cmd.append(task_folder_path)
        
        # 添加tif路径（第3个参数）
        tif_path = _get_tif_path_for_task(task_uuid, task_data, point_config)
        if tif_path:
            cmd.append(tif_path)
        else:
            current_app.logger.warning(f"未找到tif路径，任务可能无法正常运行")
            # 添加一个默认的空字符串，避免参数缺失
            cmd.append("")
        
        current_app.logger.info(f"启动预测任务 {task_uuid}")
        current_app.logger.info(f"任务文件夹: {task_folder_path}")
        current_app.logger.info(f"Python解释器: {python_exe}")
        current_app.logger.info(f"脚本路径: {script_path}")
        current_app.logger.info(f"工作目录: {work_dir}")
        current_app.logger.info(f"输入文件: {input_csv_path}")
        current_app.logger.info(f"输出路径: {output_csv_path}")
        current_app.logger.info(f"TIF路径: {tif_path}")
        current_app.logger.info(f"完整命令: {' '.join(cmd)}")
        
        # 启动进程
        if _process_manager.start_process(task_uuid, cmd, work_dir, env, _on_process_complete):
            return {
                'status': OnlineDeductionStatus.IN_PROGRESS.value,
                'message': '任务已启动',
                'start_time': datetime.now().isoformat(),
                'output_csv_path': output_csv_path,
                'command': ' '.join(cmd),
                'work_dir': work_dir
            }
        else:
            raise RuntimeError("启动预测任务失败")
            
    except Exception as e:
        current_app.logger.error(f"运行预测模型失败: {str(e)}")
        raise e


def get_task_status_service(task_uuid: str) -> Tuple[Optional[Dict], Optional[str]]:
    """
    获取任务状态
    """
    try:
        if task_uuid not in TASK_STATUS_STORE:
            return None, f"Task {task_uuid} not found"
        
        task_info = TASK_STATUS_STORE[task_uuid].copy()
        
        # 获取进程状态
        process_status = _process_manager.get_process_status(task_uuid)
        if process_status:
            task_info['process_status'] = process_status
        
        return task_info, None
        
    except Exception as e:
        current_app.logger.error(f"Error getting task status: {str(e)}")
        return None, f"Error getting task status: {str(e)}"


def get_task_result_service(task_uuid: str) -> Tuple[Optional[Dict], Optional[str]]:
    """
    获取任务结果
    """
    try:
        if task_uuid not in TASK_STATUS_STORE:
            return None, f"Task {task_uuid} not found"
        
        task_info = TASK_STATUS_STORE[task_uuid]
        
        # 检查任务状态
        if task_info['status'] == OnlineDeductionStatus.COMPLETED.value:
            # 任务完成，返回结果
            result = {
                'task_uuid': task_uuid,
                'status': task_info['status'],
                'message': task_info['message'],
                'result_csv_content': task_info.get('result_csv_content', ''),
                'completed_at': task_info.get('end_time')
            }
            return result, None
        elif task_info['status'] == OnlineDeductionStatus.IN_PROGRESS.value:
            # 任务进行中
            result = {
                'task_uuid': task_uuid,
                'status': task_info['status'],
                'message': '任务正在进行中，请稍后查询结果',
                'started_at': task_info.get('start_time')
            }
            return result, None
        else:
            # 任务失败或其他状态
            result = {
                'task_uuid': task_uuid,
                'status': task_info['status'],
                'message': task_info['message']
            }
            return result, None
            
    except Exception as e:
        current_app.logger.error(f"Error getting task result: {str(e)}")
        return None, f"Error getting task result: {str(e)}"


def stop_task_service(task_uuid: str) -> Tuple[Optional[Dict], Optional[str]]:
    """
    停止任务
    """
    try:
        if task_uuid not in TASK_STATUS_STORE:
            return None, f"Task {task_uuid} not found"
        
        task_info = TASK_STATUS_STORE[task_uuid]
        
        # 只能停止正在进行中的任务
        if task_info['status'] != OnlineDeductionStatus.IN_PROGRESS.value:
            return None, f"Task {task_uuid} is not running"
        
        # 停止进程
        success = _process_manager.stop_process(task_uuid)
        
        if success:
            task_info['status'] = OnlineDeductionStatus.ABORTED.value
            task_info['message'] = '任务已被手动停止'
            task_info['end_time'] = datetime.now().isoformat()
            TASK_STATUS_STORE[task_uuid] = task_info
            
            result = {
                'task_uuid': task_uuid,
                'status': task_info['status'],
                'message': task_info['message']
            }
            return result, None
        else:
            return None, f"Failed to stop task {task_uuid}"
            
    except Exception as e:
        current_app.logger.error(f"Error stopping task: {str(e)}")
        return None, f"Error stopping task: {str(e)}"


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


def _get_tif_path_for_task(task_uuid: str, task_data: Dict[str, Any], point_config: Dict[str, Any]) -> Optional[str]:
    """
    获取任务所需的tif文件路径
    
    Args:
        task_uuid: 任务UUID
        task_data: 任务数据
        point_config: 点位配置信息
    
    Returns:
        tif目录路径，如果找不到则返回None
    """
    try:
        scenario_type = task_data.get('scenario_type')
        
        if scenario_type == 'typical_scenario':
            # 典型场景：从元信息中获取tif_image_name（实际是tif子目录名）
            scenario_info = point_config.get('scenario_info', {})
            tif_image_name = scenario_info.get('tif_image_name')
            
            if not tif_image_name:
                current_app.logger.warning(f"典型场景缺少tif_image_name字段")
                return None
            
            # 构建tif子目录路径
            tif_dir_path = os.path.join(
                current_app.config.get('STORAGE_FOLDER'),
                'tif',
                tif_image_name
            )
            
            # 检查tif子目录是否存在
            if os.path.exists(tif_dir_path) and os.path.isdir(tif_dir_path):
                current_app.logger.info(f"找到tif目录: {tif_dir_path}")
                return tif_dir_path
            
            current_app.logger.warning(f"未找到tif目录: {tif_dir_path}")
            return None
            
        else:
            # 非典型场景：使用默认的tif目录
            current_app.logger.info(f"非典型场景，使用默认tif目录")
            
            # 使用默认的tif子目录（可以是nanjing作为默认值）
            default_tif_dir = os.path.join(
                current_app.config.get('STORAGE_FOLDER'),
                'tif',
                'nanjing'  # 默认使用nanjing目录
            )
            
            if os.path.exists(default_tif_dir):
                current_app.logger.info(f"使用默认tif目录: {default_tif_dir}")
                return default_tif_dir
            
            current_app.logger.warning(f"默认tif目录不存在: {default_tif_dir}")
            return None
            
    except Exception as e:
        current_app.logger.error(f"获取tif路径时发生错误: {str(e)}")
        return None 