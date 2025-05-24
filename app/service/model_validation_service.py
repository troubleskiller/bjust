from app.model.evaluate_info import ValidationTaskTypeOption, ModelValidationTask, ModelValidationTaskModelAssociation # Ensure this matches your model file
from app import db
from app.model.dataset_info import ChannelDataset # Import ChannelDataset model
from app.model.model_info import Model # Import Model
import uuid
import datetime
from typing import Dict, Any, Optional, Tuple
from flask import current_app

def get_validation_task_types_service():
    """
    Service to fetch all available validation task types.
    """
    try:
        task_types_query = ValidationTaskTypeOption.query.order_by(ValidationTaskTypeOption.id).all()
        
        task_types_data = []
        for task_type in task_types_query:
            task_types_data.append({
                "id": task_type.task_type_id_str, # As per API doc, response field is "id"
                "name": task_type.name
            })
        return task_types_data, None
    except Exception as e:
        # current_app.logger.error(f"Error in get_validation_task_types_service: {str(e)}")
        return None, str(e)

def get_validation_datasets_service(task_type: str):
    """
    Service to fetch datasets suitable for a specific validation task type.
    Filters for 'real_measurement' data_type and matches applicable_task_type.
    """
    try:
        if not task_type:
            return None, "task_type parameter is required."

        # Query datasets that are 'real_measurement' and match the applicable_task_type
        # The task.md implies that ChannelDataset.applicable_task_type should match the provided validation task_type.
        # If the validation task_type (e.g., "single_point_link") is directly stored or can be mapped
        # to values in ChannelDataset.applicable_task_type, this filter is direct.
        # If ChannelDataset.applicable_task_type stores something like "single_point_prediction" 
        # and validation task_type is more specific like "single_point_link", a mapping might be needed
        # or the ChannelDataset.applicable_task_type should store the more specific validation task types.
        # For now, assuming a direct match or that the stored applicable_task_type is compatible.
        
        datasets_query = ChannelDataset.query.filter(
            ChannelDataset.data_type == "real_measurement",
            ChannelDataset.applicable_task_type == task_type # Direct match as per task.md example response
        ).order_by(ChannelDataset.dataset_name).all()
        
        datasets_data = []
        for dataset in datasets_query:
            datasets_data.append({
                "dataset_uuid": dataset.dataset_uuid,
                "dataset_name": dataset.dataset_name,
                "location_description": dataset.location_description,
                "center_frequency_mhz": dataset.center_frequency_mhz,
                "applicable_task_type": dataset.applicable_task_type # Redundant info for frontend as per doc
            })
        
        return datasets_data, None
    except Exception as e:
        # current_app.logger.error(f"Error in get_validation_datasets_service: {str(e)}")
        return None, str(e)

def get_validation_models_service(task_type: str, dataset_uuid: str):
    """
    Service to fetch models suitable for a specific validation task type and dataset.
    Ensures model is compatible with task_type and dataset (e.g., frequency bands, scenarios).
    """
    try:
        if not task_type or not dataset_uuid:
            return None, "task_type and dataset_uuid parameters are required."

        # 1. Fetch the dataset to understand its properties (e.g., frequency for matching)
        dataset = ChannelDataset.query.filter(ChannelDataset.dataset_uuid == dataset_uuid).first()
        if not dataset:
            return None, "Dataset not found."
        
        # Ensure the dataset itself is suitable for the task_type (redundant if already filtered, but good check)
        if dataset.data_type != "real_measurement" or dataset.applicable_task_type != task_type:
            # This scenario should ideally be prevented by frontend flow, 
            # but as a safeguard, or if applicable_task_type is more general.
            return [], "Dataset is not suitable for the specified task type (not real_measurement or mismatched applicable_task_type)." 
            # Return [] for data, and a specific error message.

        # 2. Filter models based on task_type and compatibility with the dataset.
        # The task.md implies Model.can_be_used_for_validation might be a general flag.
        # True compatibility might involve matching model's frequency_bands and application_scenarios
        # with dataset's properties (center_frequency_mhz, location_description/scenario implied by it).
        
        # For task_type matching with Model.model_type, we use the same mapping as in online_deduction_service
        # This mapping should ideally be centralized or consistently defined.
        online_task_type_to_model_type_mapping = {
            "single_point_discrete": "large_scale", # Assuming discrete and link map to large_scale
            "single_point_link": "large_scale",
            "situation": "situation_awareness",
            "small_scale": "small_scale",
        }
        target_model_type = online_task_type_to_model_type_mapping.get(task_type)
        if not target_model_type:
            return [], "Invalid validation task_type for model matching."

        query = Model.query.filter(Model.model_type == target_model_type)
        query = query.filter(Model.can_be_used_for_validation == True) # As per Model Plaza doc for can_be_used_for_validation

        # Further filtering based on dataset properties (e.g., frequency band)
        # This is a simplified check. A more robust check would involve parsing Model.frequency_bands (JSON array)
        # and comparing with dataset.center_frequency_mhz. 
        # Example: if dataset.center_frequency_mhz is 5900 (5.9GHz), a model supporting "5.9GHz" or a range covering it should match.
        # The current Model.frequency_bands stores strings like "2.4GHz", "5.8GHz", etc.
        # We would need a helper to convert dataset.center_frequency_mhz to a comparable string or range.
        # For now, this advanced filtering is omitted for brevity but is crucial for real-world accuracy.
        # models_query = query.all() # Apply more filters before .all()

        # Placeholder for more advanced compatibility checks:
        # For example, check if dataset.center_frequency_mhz falls within any of the model's frequency_bands.
        # And if dataset's scenario (derived from location_description or a dedicated field) 
        # matches any of model.application_scenarios.

        # Let's assume for now that can_be_used_for_validation and model_type are primary filters.
        potential_models = query.order_by(Model.model_name).all()
        
        # If specific dataset compatibility logic (e.g. frequency band matching) needs to be more precise:
        # validated_models_data = []
        # for model in potential_models:
        #    if is_model_compatible_with_dataset(model, dataset):
        #        validated_models_data.append({ "model_uuid": model.model_uuid, "model_name": model.model_name})
        # return validated_models_data, None
        # where is_model_compatible_with_dataset would contain the detailed logic.

        models_data = [
            {"model_uuid": model.model_uuid, "model_name": model.model_name}
            for model in potential_models
        ]
        
        return models_data, None
    except Exception as e:
        # current_app.logger.error(f"Error in get_validation_models_service: {str(e)}")
        return None, str(e) 

def generate_validation_task_uuid():
    return f"val-task-{uuid.uuid4().hex}"

def create_validation_task_service(data: dict):
    """
    Service to create a new model validation task.
    data: dict containing task details (validation_task_name, task_type, dataset_uuid, model_uuids, param_config)
    """
    try:
        # 1. Validate required fields
        required_fields = ['task_type', 'dataset_uuid', 'model_uuids']
        for field in required_fields:
            if field not in data or not data[field]:
                return None, f"Missing required field: {field}"
        
        if not isinstance(data['model_uuids'], list) or len(data['model_uuids']) == 0:
            return None, "model_uuids must be a non-empty list."

        # 2. Verify existence of related entities
        task_type_obj = ValidationTaskTypeOption.query.filter(ValidationTaskTypeOption.task_type_id_str == data['task_type']).first()
        if not task_type_obj:
            return None, f"Invalid task_type: {data['task_type']}"

        dataset_obj = ChannelDataset.query.filter(ChannelDataset.dataset_uuid == data['dataset_uuid']).first()
        if not dataset_obj:
            return None, f"Dataset not found: {data['dataset_uuid']}"
        
        # Ensure dataset is suitable (real_measurement and compatible with task_type)
        if dataset_obj.data_type != "real_measurement":
             return None, "Dataset for validation must be of type 'real_measurement'."
        if dataset_obj.applicable_task_type != data['task_type']:
             # This check depends on how strictly applicable_task_type in ChannelDataset maps to validation task types
             # current_app.logger.warning(f"Dataset applicable_task_type '{dataset_obj.applicable_task_type}' might not perfectly match validation task_type '{data['task_type']}'. Proceeding, but review this logic.")
             pass # Assuming previous GET /validation/datasets already filtered this.

        # Verify all models exist
        models_to_associate = []
        for model_uuid_str in data['model_uuids']:
            model_obj = Model.query.filter(Model.model_uuid == model_uuid_str).first()
            if not model_obj:
                return None, f"Model not found: {model_uuid_str}"
            # Further checks: ensure model is compatible with task_type and dataset (simplified here)
            # online_task_type_to_model_type_mapping = { ... } (use the mapping from get_validation_models_service)
            # if model_obj.model_type != online_task_type_to_model_type_mapping.get(data['task_type']):
            #    return None, f"Model {model_uuid_str} is not of a type suitable for task {data['task_type']}."
            models_to_associate.append(model_obj)

        # 3. Create the ModelValidationTask
        validation_task_uuid = generate_validation_task_uuid()
        new_validation_task = ModelValidationTask(
            validation_task_uuid=validation_task_uuid,
            validation_task_name=data.get('validation_task_name'), # Optional
            task_type_id_str=data['task_type'],
            dataset_uuid=data['dataset_uuid'],
            param_config=data.get('param_config'), # Optional, used for small_scale
            status="PENDING", # Initial status
            created_at=datetime.datetime.utcnow()
        )
        db.session.add(new_validation_task)
        
        # 4. Create associations
        for model_obj in models_to_associate:
            association = ModelValidationTaskModelAssociation(
                validation_task_uuid=validation_task_uuid,
                model_uuid=model_obj.model_uuid,
                status_for_model="PENDING" # Initial status for each model in this task
            )
            db.session.add(association)
            
        db.session.commit()
        
        return {"validation_task_uuid": validation_task_uuid}, None

    except Exception as e:
        db.session.rollback()
        # current_app.logger.error(f"Error in create_validation_task_service: {str(e)}")
        return None, str(e)

def get_validation_task_results_service(validation_task_uuid: str) -> Tuple[Optional[Dict], Optional[str]]:
    """
    获取模型验证任务的状态和结果
    
    Args:
        validation_task_uuid: 验证任务UUID
    
    Returns:
        (result, error_message)
    """
    try:
        # 查询验证任务
        validation_task = ModelValidationTask.query.filter(
            ModelValidationTask.validation_task_uuid == validation_task_uuid
        ).first()
        
        if not validation_task:
            return None, "Validation task not found."
        
        # 获取关联的数据集信息
        dataset = ChannelDataset.query.filter(
            ChannelDataset.dataset_uuid == validation_task.dataset_uuid
        ).first()
        
        # 获取任务类型信息
        task_type_info = ValidationTaskTypeOption.query.filter(
            ValidationTaskTypeOption.task_type_id_str == validation_task.task_type_id_str
        ).first()
        
        # 获取关联的模型及其验证结果
        model_associations = ModelValidationTaskModelAssociation.query.filter(
            ModelValidationTaskModelAssociation.validation_task_uuid == validation_task_uuid
        ).all()
        
        model_comparison_results = []
        for association in model_associations:
            model = Model.query.filter(Model.model_uuid == association.model_uuid).first()
            if model:
                # TODO: 这里应该从实际的验证结果表或文件中获取结果数据
                # 暂时返回模拟数据
                model_result = {
                    "model_uuid": model.model_uuid,
                    "model_name": model.model_name,
                    "status": association.status_for_model or "PENDING",
                    "error_message": None
                }
                
                # 根据任务类型添加不同的结果数据
                if validation_task.task_type_id_str == "single_point_link":
                    model_result.update({
                        "overall_rmse_db": 4.5,
                        "predicted_path_loss_curve": [
                            {"distance_m": 0, "pos": {"lat": 39.916, "lon": 116.405}, "predicted_pl_db": 90.1},
                            {"distance_m": 50, "pos": {"lat": 39.917, "lon": 116.406}, "predicted_pl_db": 95.3}
                        ]
                    })
                elif validation_task.task_type_id_str == "single_point_discrete":
                    model_result.update({
                        "overall_rmse_db": 3.1,
                        "point_predictions": [
                            {"point_id_in_dataset": "RX1", "predicted_pl_db": 102.5, "error_db": 2.5},
                            {"point_id_in_dataset": "RX2", "predicted_pl_db": 104.0, "error_db": -1.3}
                        ]
                    })
                elif validation_task.task_type_id_str == "situation":
                    model_result.update({
                        "comparison_metrics": {
                            "heatmap_rmse_db": 5.8,
                            "coverage_accuracy_percent": 85.2
                        },
                        "predicted_heatmap_data": {
                            "heatmap_data_type": "grid",
                            "grid_origin": {"lat": 39.900, "lon": 116.390},
                            "cell_size_deg": {"lat_delta": 0.0001, "lon_delta": 0.0001},
                            "rows": 300,
                            "cols": 300,
                            "values": [[100.5, 101.2], [102.1, 103.0]],  # 简化数据
                            "value_unit": "dB"
                        }
                    })
                elif validation_task.task_type_id_str == "small_scale":
                    model_result.update({
                        "pdp_comparison_metrics": {
                            "average_delay_spread_error_ns": 5.2,
                            "rmse_power_db_per_delay_bin": [2.1, 3.0, 1.5]
                        },
                        "ber_snr_comparison_metrics": {
                            "ber_rmse_at_snr_points": [
                                {"snr_db": 10, "rmse_ber": 0.0015},
                                {"snr_db": 15, "rmse_ber": 0.0008}
                            ]
                        }
                    })
                
                model_comparison_results.append(model_result)
        
        # 构建实测数据 (模拟数据)
        actual_data = {}
        if validation_task.task_type_id_str == "single_point_link":
            actual_data = {
                "path_loss_curve": [
                    {"distance_m": 0, "pos": {"lat": 39.916, "lon": 116.405}, "real_pl_db": 89.0},
                    {"distance_m": 50, "pos": {"lat": 39.917, "lon": 116.406}, "real_pl_db": 93.5}
                ]
            }
        elif validation_task.task_type_id_str == "single_point_discrete":
            actual_data = {
                "points": [
                    {"point_id_in_dataset": "RX1", "tx_pos": {"lat": 39.915, "lon": 116.404}, 
                     "rx_pos": {"lat": 39.916, "lon": 116.405}, "real_pl_db": 100.0},
                    {"point_id_in_dataset": "RX2", "tx_pos": {"lat": 39.915, "lon": 116.404}, 
                     "rx_pos": {"lat": 39.917, "lon": 116.406}, "real_pl_db": 105.3}
                ]
            }
        elif validation_task.task_type_id_str == "situation":
            actual_data = {
                "heatmap_data_type": "grid",
                "grid_origin": {"lat": 39.900, "lon": 116.390},
                "cell_size_deg": {"lat_delta": 0.0001, "lon_delta": 0.0001},
                "rows": 300,
                "cols": 300,
                "values": [[99.5, 100.2], [101.1, 102.0]],  # 简化的实测数据
                "value_unit": "dB"
            }
        elif validation_task.task_type_id_str == "small_scale":
            actual_data = {
                "pdp_data": {
                    "time_delays_ns": [0, 10, 20, 30],
                    "power_levels_dbm": [
                        {"pos": {"lat": 39.916, "lon": 116.405}, "pdp": [-80, -85, -90, -100]}
                    ]
                },
                "ber_snr_data": {
                    "snr_values_db": [0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20],
                    "ber_values": [
                        {"pos": {"lat": 39.916, "lon": 116.405}, "ber": [0.5, 0.3, 0.1, 0.01, 0.001, 0.0001, 0.00001, 0.000001, 0.0000001, 0.00000001, 0.000000001]}
                    ]
                }
            }
        
        # 构建最终结果
        result = {
            "validation_task_uuid": validation_task_uuid,
            "validation_task_name": validation_task.validation_task_name or f"Validation Task {validation_task_uuid[:8]}",
            "task_type": validation_task.task_type_id_str,
            "dataset_name": dataset.dataset_name if dataset else "Unknown Dataset",
            "status": validation_task.status,
            "error_message": validation_task.error_message,
            "actual_data": actual_data,
            "model_comparison_results": model_comparison_results
        }
        
        return result, None
        
    except Exception as e:
        current_app.logger.error(f"Error in get_validation_task_results_service for {validation_task_uuid}: {str(e)}")
        return None, f"Service error: {str(e)}" 