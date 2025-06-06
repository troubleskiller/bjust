from flask import Blueprint, jsonify, current_app, request
from werkzeug.utils import secure_filename
import os
import tempfile
from app.service.typical_scenario_service import (
    add_typical_scenario_service,
    get_typical_scenario_info_service,
    list_all_typical_scenarios_service,
    list_typical_scenarios_by_type_service,
    delete_typical_scenario_service,
    get_available_prediction_types
)

typical_scenario_bp = Blueprint('typical_scenario_bp', __name__, url_prefix='/api/v1/typical_scenarios')

@typical_scenario_bp.route('/prediction_types', methods=['GET'])
def get_prediction_types_route():
    """
    Get Available Prediction Types
    ---
    tags:
      - Typical Scenario Management
    responses:
      200:
        description: List of available prediction types
        content:
          application/json:
            schema:
              type: object
              properties:
                code: { type: string, example: "200" }
                message: { type: string, example: "success" }
                data:
                  type: array
                  items:
                    type: string
                  example: ["单点预测", "动态感知", "小尺度预测"]
      500:
        description: Internal server error
    """
    try:
        prediction_types = get_available_prediction_types()
        return jsonify({"message": "success", "code": "200", "data": prediction_types}), 200
    except Exception as e:
        current_app.logger.error(f"Unexpected error in get_prediction_types_route: {str(e)}")
        return jsonify({"message": "An unexpected error occurred.", "code": "500"}), 500

@typical_scenario_bp.route('', methods=['POST'])
def add_typical_scenario_route():
    """
    Add Typical Scenario
    ---
    tags:
      - Typical Scenario Management
    requestBody:
      required: true
      content:
        multipart/form-data:
          schema:
            type: object
            required:
              - scenario_name
              - prediction_type
              - tif_image_name
              - input_file
            properties:
              scenario_name:
                type: string
                description: 典型场景名称
                example: "新工业园区"
              prediction_type:
                type: string
                description: 预测类型
                enum: ["单点预测", "动态感知", "小尺度预测"]
                example: "单点预测"
              tif_image_name:
                type: string
                description: tif图像文件名称
                example: "nanjing"
              input_file:
                type: string
                format: binary
                description: input CSV文件，包含场景的具体配置数据
    responses:
      200:
        description: Typical scenario added successfully
        content:
          application/json:
            schema:
              type: object
              properties:
                code: { type: string, example: "200" }
                message: { type: string, example: "success" }
                data:
                  type: object
                  properties:
                    scenario_uuid: { type: string }
                    folder_name: { type: string }
                    scenario_name: { type: string }
                    prediction_type: { type: string }
                    scenario_directory: { type: string }
                    input_file: { type: string }
                    tif_image_name: { type: string }
                    created_at: { type: string }
      400:
        description: Bad request (missing fields or invalid data)
      500:
        description: Internal server error
    """
    try:
        # 检查请求中的表单数据
        scenario_name = request.form.get('scenario_name')
        prediction_type = request.form.get('prediction_type')
        tif_image_name = request.form.get('tif_image_name')
        
        if not scenario_name:
            return jsonify({"message": "scenario_name is required", "code": "400"}), 400
        
        if not prediction_type:
            return jsonify({"message": "prediction_type is required", "code": "400"}), 400
        
        if not tif_image_name:
            return jsonify({"message": "tif_image_name is required", "code": "400"}), 400
        
        # 检查上传的文件
        if 'input_file' not in request.files:
            return jsonify({"message": "input_file is required", "code": "400"}), 400
        
        file = request.files['input_file']
        if file.filename == '':
            return jsonify({"message": "No file selected", "code": "400"}), 400
        
        # 保存上传的文件到临时位置
        if file:
            filename = secure_filename(file.filename)
            temp_dir = tempfile.mkdtemp()
            temp_file_path = os.path.join(temp_dir, filename)
            file.save(temp_file_path)
            
            try:
                # 调用服务层添加典型场景
                result, error = add_typical_scenario_service(scenario_name, prediction_type, tif_image_name, temp_file_path)
                
                if error:
                    return jsonify({"message": error, "code": "400"}), 400
                
                return jsonify({"message": "success", "code": "200", "data": result}), 200
                
            finally:
                # 清理临时文件
                try:
                    os.remove(temp_file_path)
                    os.rmdir(temp_dir)
                except:
                    pass
    
    except Exception as e:
        current_app.logger.error(f"Unexpected error in add_typical_scenario_route: {str(e)}")
        return jsonify({"message": "An unexpected error occurred.", "code": "500"}), 500

@typical_scenario_bp.route('', methods=['GET'])
def list_typical_scenarios_route():
    """
    List All Typical Scenarios or Filter by Prediction Type
    ---
    tags:
      - Typical Scenario Management
    parameters:
      - name: prediction_type
        in: query
        required: false
        description: 预测类型过滤器（可选）
        schema:
          type: string
          enum: ["单点预测", "动态感知", "小尺度预测"]
        example: "单点预测"
    responses:
      200:
        description: List of typical scenarios (all or filtered by type)
        content:
          application/json:
            schema:
              type: object
              properties:
                code: { type: string, example: "200" }
                message: { type: string, example: "success" }
                data:
                  type: object
                  properties:
                    scenarios:
                      type: array
                      items:
                        type: object
                        properties:
                          folder_name: { type: string }
                          uuid: { type: string }
                          name: { type: string }
                          prediction_type: { type: string }
                          prediction_type_code: { type: string }
                          tif_image_name: { type: string }
                          created_at: { type: string }
                          type: { type: string }
                    prediction_type: { type: string, description: "当使用类型过滤时返回" }
                    prediction_type_code: { type: string, description: "当使用类型过滤时返回" }
                    scenarios_by_type:
                      type: object
                      description: 按预测类型分组的场景（仅在获取所有场景时返回）
                    total_count: { type: integer }
      400:
        description: Invalid prediction_type parameter
      500:
        description: Internal server error
    """
    try:
        # 检查是否有预测类型过滤参数
        prediction_type = request.args.get('prediction_type')
        
        if prediction_type:
            # 按类型过滤
            result, error = list_typical_scenarios_by_type_service(prediction_type)
            if error:
                # 检查是否是无效的预测类型
                if "Invalid prediction_type" in error:
                    return jsonify({"message": error, "code": "400"}), 400
                
                current_app.logger.error(f"Error listing scenarios by type: {error}")
                return jsonify({"message": error, "code": "500"}), 500
        else:
            # 获取所有场景
            result, error = list_all_typical_scenarios_service()
            if error:
                current_app.logger.error(f"Error listing all scenarios: {error}")
                return jsonify({"message": error, "code": "500"}), 500
        
        return jsonify({"message": "success", "code": "200", "data": result}), 200
    
    except Exception as e:
        current_app.logger.error(f"Unexpected error in list_typical_scenarios_route: {str(e)}")
        return jsonify({"message": "An unexpected error occurred.", "code": "500"}), 500

@typical_scenario_bp.route('/<string:scenario_name>', methods=['GET'])
def get_typical_scenario_info_route(scenario_name: str):
    """
    Get Typical Scenario Information
    ---
    tags:
      - Typical Scenario Management
    parameters:
      - name: scenario_name
        in: path
        required: true
        description: 典型场景名称、文件夹名称或UUID
        schema:
          type: string
    responses:
      200:
        description: Typical scenario information
        content:
          application/json:
            schema:
              type: object
              properties:
                code: { type: string, example: "200" }
                message: { type: string, example: "success" }
                data:
                  type: object
                  properties:
                    scenario_uuid: { type: string }
                    folder_name: { type: string }
                    scenario_name: { type: string }
                    prediction_type: { type: string }
                    prediction_type_code: { type: string }
                    tif_image_name: { type: string }
                    created_at: { type: string }
                    files: { type: array }
      404:
        description: Typical scenario not found
      500:
        description: Internal server error
    """
    try:
        result, error = get_typical_scenario_info_service(scenario_name)
        
        if error:
            if "not found" in error.lower():
                return jsonify({"message": error, "code": "404"}), 404
            
            current_app.logger.error(f"Error getting typical scenario info: {error}")
            return jsonify({"message": error, "code": "500"}), 500
        
        return jsonify({"message": "success", "code": "200", "data": result}), 200
    
    except Exception as e:
        current_app.logger.error(f"Unexpected error in get_typical_scenario_info_route: {str(e)}")
        return jsonify({"message": "An unexpected error occurred.", "code": "500"}), 500

@typical_scenario_bp.route('/<string:scenario_name>', methods=['DELETE'])
def delete_typical_scenario_route(scenario_name: str):
    """
    Delete Typical Scenario
    ---
    tags:
      - Typical Scenario Management
    parameters:
      - name: scenario_name
        in: path
        required: true
        description: 典型场景名称、文件夹名称或UUID
        schema:
          type: string
    responses:
      200:
        description: Typical scenario deleted successfully
        content:
          application/json:
            schema:
              type: object
              properties:
                code: { type: string, example: "200" }
                message: { type: string, example: "success" }
                data:
                  type: object
                  properties:
                    scenario_uuid: { type: string }
                    folder_name: { type: string }
                    scenario_name: { type: string }
                    prediction_type: { type: string }
                    deleted_at: { type: string }
      404:
        description: Typical scenario not found
      500:
        description: Internal server error
    """
    try:
        result, error = delete_typical_scenario_service(scenario_name)
        
        if error:
            if "not found" in error.lower():
                return jsonify({"message": error, "code": "404"}), 404
            
            current_app.logger.error(f"Error deleting typical scenario: {error}")
            return jsonify({"message": error, "code": "500"}), 500
        
        return jsonify({"message": "success", "code": "200", "data": result}), 200
    
    except Exception as e:
        current_app.logger.error(f"Unexpected error in delete_typical_scenario_route: {str(e)}")
        return jsonify({"message": "An unexpected error occurred.", "code": "500"}), 500 