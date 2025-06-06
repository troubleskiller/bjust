from flask import Blueprint, jsonify, current_app, request
from app.service.online_deduction_service import (
    get_online_models_by_task_type_service, 
    create_prediction_task_service, 
    get_prediction_task_result_service, 
    get_available_typical_scenarios,
    get_task_status_service,
    get_task_result_service,
    stop_task_service
)

online_deduction_bp = Blueprint('online_deduction_bp', __name__, url_prefix='/api/v1/online_deduction')

@online_deduction_bp.route('/models', methods=['GET'])
def get_online_models_by_task_type_route():
    """
    Get Model List by Task Type for Online Deduction
    ---
    tags:
      - Online Deduction - Common
    parameters:
      - name: task_type
        in: query
        required: true
        description: Type of the task ("single_point_prediction", "situation_prediction", "small_scale_prediction")
        schema:
          type: string
          enum: ["single_point_prediction", "situation_prediction", "small_scale_prediction"]
    responses:
      200:
        description: A list of models suitable for the task type.
        content:
          application/json:
            schema:
              type: object
              properties:
                code:
                  type: string
                  example: "200"
                message:
                  type: string
                  example: "success"
                data:
                  type: array
                  items:
                    type: object
                    properties:
                      model_uuid:
                        type: string
                        example: "uuid-model-001"
                      model_name:
                        type: string
                        example: "RayTracer-Pro"
                      model_description:
                        type: string
                        example: "基于射线追踪的精确信道模型。"
                      model_img:
                        type: string
                        example: "/storage/models/raytracer_pro_thumb.jpg"
                      model_doc_url:
                        type: string
                        example: "/models/uuid-model-001/documentation"
      400:
        description: Invalid or missing task_type.
      500:
        description: Internal server error.
    """
    task_type = request.args.get('task_type')
    if not task_type:
        return jsonify({"message": "task_type query parameter is required", "code": "400", "data": None}), 400

    try:
        models, error = get_online_models_by_task_type_service(task_type)
        
        if error and not models: # Indicates a more significant error like DB issue
             current_app.logger.error(f"Error fetching models for task type '{task_type}': {error}")
             return jsonify({"message": f"Failed to retrieve models: {error}", "code": "500", "data": None}), 500
        
        if error: # Could be an invalid task_type leading to an empty list but with an error message
            return jsonify({"message": error, "code": "400", "data": []}), 400

        return jsonify({"message": "success", "code": "200", "data": models}), 200
    except Exception as e:
        current_app.logger.error(f"Exception in get_online_models_by_task_type_route for task_type '{task_type}': {str(e)}")
        return jsonify({"message": "An unexpected error occurred", "code": "500", "data": None}), 500

@online_deduction_bp.route('/tasks', methods=['POST'])
def create_prediction_task_route():
    """
    Create Prediction Task - Unified Interface
    ---
    tags:
      - Online Deduction - Common
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            required:
              - model_uuid
              - prediction_mode
              - scenario_type
              - point_config
              - param_config
            properties:
              model_uuid:
                type: string
                example: "uuid-model-001"
              prediction_mode:
                type: string
                enum: ["point", "link", "situation", "small_scale"]
                example: "link"
              scenario_type:
                type: string
                enum: ["manual_selection", "typical_scenario", "custom_upload"]
                example: "manual_selection"
                description: "场景选择类型：manual_selection(自主选点), typical_scenario(典型场景), custom_upload(自定义上传)"
              point_config:
                type: object
                properties:
                  # 自主选点和自定义上传时使用
                  scenario_description:
                    type: string
                    example: "城市商业区信号覆盖预测"
                    description: "场景描述字符串（自主选点和自定义上传时使用）"
                  # 典型场景时使用
                  scenario_uuid:
                    type: string
                    example: "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
                    description: "典型场景UUID（典型场景时使用）"
                  # 原有的点位配置（手动指定点位时使用）
                  tx_pos_list:
                    type: array
                    items:
                      type: object
                      properties:
                        lat: { type: number, format: float }
                        lon: { type: number, format: float }
                        height: { type: number, format: float }
                  rx_pos_list:
                    type: array
                    items:
                      type: object
                      properties:
                        lat: { type: number, format: float }
                        lon: { type: number, format: float }
                        height: { type: number, format: float }
                  area_bounds:
                    type: object
                    properties:
                      min_lat: { type: number, format: float }
                      min_lon: { type: number, format: float }
                      max_lat: { type: number, format: float }
                      max_lon: { type: number, format: float }
                  resolution_m:
                    type: number
                    format: float
              param_config:
                type: object
                properties:
                  frequency_band: { type: string }
                  modulation_mode: { type: string }
                  modulation_order: { type: integer }
    responses:
      200:
        description: Task created successfully.
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
                    task_uuid: { type: string }
                    task_folder_name: 
                      type: string
                      description: "任务文件夹名称，格式：ONLINE-DEDUCTION-{uuid}"
                      example: "ONLINE-DEDUCTION-12345678-1234-1234-1234-123456789abc"
                    task_folder_path:
                      type: string
                      description: "任务文件夹完整路径"
                      example: "/storage/tasks/ONLINE-DEDUCTION-12345678-1234-1234-1234-123456789abc"
                    prediction_mode: { type: string }
                    scenario_type: { type: string }
                    status: 
                      type: string
                      enum: ["NOT_STARTED", "IN_PROGRESS", "COMPLETED", "ABORTED"]
                      description: "任务状态"
                    message:
                      type: string
                      description: "任务状态描述"
                    scenario_csv_content: 
                      type: string
                      description: "典型场景的input.csv文件内容（仅当scenario_type为typical_scenario时返回）"
                      example: "39.9200,116.4200,30.0,39.9195,116.4195,1.5\n39.9200,116.4200,30.0,39.9205,116.4205,1.5"
                    scenario_info:
                      type: object
                      description: "典型场景的元信息（仅当scenario_type为typical_scenario时返回）"
                      properties:
                        scenario_name: { type: string }
                        prediction_type: { type: string }
                        tif_image_name: { type: string }
                        created_at: { type: string }
      400:
        description: Bad request (invalid data, missing fields).
      500:
        description: Internal server error.
    """
    if not request.is_json:
        return jsonify({"message": "Request must be JSON", "code": "400"}), 400

    data = request.get_json()
    if not data:
        return jsonify({"message": "No input data provided", "code": "400"}), 400

    # Basic validation
    required_fields = ['model_uuid', 'prediction_mode', 'scenario_type', 'point_config', 'param_config']
    for field in required_fields:
        if field not in data:
            return jsonify({"message": f"Missing required field: {field}", "code": "400"}), 400

    try:
        result, error = create_prediction_task_service(data)

        if error:
            if "Invalid" in error or "Missing required field" in error or "required" in error:
                return jsonify({"message": error, "code": "400"}), 400
            
            current_app.logger.error(f"Error creating prediction task: {error}")
            return jsonify({"message": f"Failed to create prediction task: {error}", "code": "500"}), 500
        
        return jsonify({"message": "success", "code": "200", "data": result}), 200

    except Exception as e:
        current_app.logger.error(f"Unexpected error in create_prediction_task_route: {str(e)}")
        return jsonify({"message": "An unexpected error occurred.", "code": "500"}), 500

@online_deduction_bp.route('/tasks/<string:task_uuid>/results', methods=['GET'])
def get_prediction_task_results_route(task_uuid: str):
    """
    Get Prediction Task Results (for point and link modes)
    ---
    tags:
      - Online Deduction - Single Point Prediction
    parameters:
      - name: task_uuid
        in: path
        required: true
        description: Task UUID
        schema:
          type: string
      - name: next_index
        in: query
        required: false
        description: Next index to fetch from (for incremental results)
        schema:
          type: integer
      - name: batch_size
        in: query
        required: false
        description: Number of points to fetch
        schema:
          type: integer
    responses:
      200:
        description: Task results
      404:
        description: Task not found
      500:
        description: Internal server error
    """
    next_index = request.args.get('next_index', type=int)
    batch_size = request.args.get('batch_size', type=int)

    try:
        result, error = get_prediction_task_result_service(task_uuid, next_index, batch_size)

        if error:
            if "not found" in error.lower():
                return jsonify({"message": error, "code": "404"}), 404
            
            current_app.logger.error(f"Error getting task results for {task_uuid}: {error}")
            return jsonify({"message": f"Failed to get task results: {error}", "code": "500"}), 500
        
        return jsonify({"message": "success", "code": "200", "data": result}), 200

    except Exception as e:
        current_app.logger.error(f"Unexpected error in get_prediction_task_results_route: {str(e)}")
        return jsonify({"message": "An unexpected error occurred.", "code": "500"}), 500

@online_deduction_bp.route('/tasks/<string:task_uuid>/result', methods=['GET'])
def get_prediction_task_result_route(task_uuid: str):
    """
    Get Prediction Task Result (for situation and small_scale modes)
    ---
    tags:
      - Online Deduction - Situation Prediction
      - Online Deduction - Small Scale Prediction
    parameters:
      - name: task_uuid
        in: path
        required: true
        description: Task UUID
        schema:
          type: string
    responses:
      200:
        description: Task result
      404:
        description: Task not found
      500:
        description: Internal server error
    """
    try:
        result, error = get_prediction_task_result_service(task_uuid, batch_mode=False)

        if error:
            if "not found" in error.lower():
                return jsonify({"message": error, "code": "404"}), 404
            
            current_app.logger.error(f"Error getting task result for {task_uuid}: {error}")
            return jsonify({"message": f"Failed to get task result: {error}", "code": "500"}), 500
        
        return jsonify({"message": "success", "code": "200", "data": result}), 200

    except Exception as e:
        current_app.logger.error(f"Unexpected error in get_prediction_task_result_route: {str(e)}")
        return jsonify({"message": "An unexpected error occurred.", "code": "500"}), 500

@online_deduction_bp.route('/typical_scenarios', methods=['GET'])
def get_typical_scenarios_route():
    """
    Get Available Typical Scenarios
    ---
    tags:
      - Online Deduction - Common
    responses:
      200:
        description: List of available typical scenarios
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
                  example: ["城市商业区", "室内办公室", "工业园区", "居民社区", "高速公路", "地铁隧道"]
      500:
        description: Internal server error
    """
    try:
        scenarios = get_available_typical_scenarios()
        return jsonify({"message": "success", "code": "200", "data": scenarios}), 200
    except Exception as e:
        current_app.logger.error(f"Unexpected error in get_typical_scenarios_route: {str(e)}")
        return jsonify({"message": "An unexpected error occurred.", "code": "500"}), 500

@online_deduction_bp.route('/tasks/<string:task_uuid>/status', methods=['GET'])
def get_task_status_route(task_uuid: str):
    """
    Get Task Status
    ---
    tags:
      - Online Deduction - Task Management
    parameters:
      - name: task_uuid
        in: path
        required: true
        description: Task UUID
        schema:
          type: string
    responses:
      200:
        description: Task status information
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
                    task_uuid: { type: string }
                    status: { type: string, enum: ["NOT_STARTED", "IN_PROGRESS", "COMPLETED", "ABORTED"] }
                    message: { type: string }
                    created_at: { type: string }
                    start_time: { type: string }
                    end_time: { type: string }
                    prediction_mode: { type: string }
                    scenario_type: { type: string }
                    process_status: { type: object }
      404:
        description: Task not found
      500:
        description: Internal server error
    """
    try:
        result, error = get_task_status_service(task_uuid)

        if error:
            if "not found" in error.lower():
                return jsonify({"message": error, "code": "404"}), 404
            
            current_app.logger.error(f"Error getting task status for {task_uuid}: {error}")
            return jsonify({"message": f"Failed to get task status: {error}", "code": "500"}), 500
        
        return jsonify({"message": "success", "code": "200", "data": result}), 200

    except Exception as e:
        current_app.logger.error(f"Unexpected error in get_task_status_route: {str(e)}")
        return jsonify({"message": "An unexpected error occurred.", "code": "500"}), 500

@online_deduction_bp.route('/tasks/<string:task_uuid>/result', methods=['GET'])
def get_task_result_route(task_uuid: str):
    """
    Get Task Result with CSV Content
    ---
    tags:
      - Online Deduction - Task Management
    parameters:
      - name: task_uuid
        in: path
        required: true
        description: Task UUID
        schema:
          type: string
    responses:
      200:
        description: Task result with CSV content
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
                    task_uuid: { type: string }
                    status: { type: string }
                    message: { type: string }
                    result_csv_content: 
                      type: string
                      description: "任务完成时返回的CSV结果字符串"
                      example: "lat,lon,height,path_loss\n39.9200,116.4200,30.0,95.5\n39.9250,116.4250,25.0,98.2"
                    completed_at: { type: string }
                    started_at: { type: string }
      404:
        description: Task not found
      500:
        description: Internal server error
    """
    try:
        result, error = get_task_result_service(task_uuid)

        if error:
            if "not found" in error.lower():
                return jsonify({"message": error, "code": "404"}), 404
            
            current_app.logger.error(f"Error getting task result for {task_uuid}: {error}")
            return jsonify({"message": f"Failed to get task result: {error}", "code": "500"}), 500
        
        return jsonify({"message": "success", "code": "200", "data": result}), 200

    except Exception as e:
        current_app.logger.error(f"Unexpected error in get_task_result_route: {str(e)}")
        return jsonify({"message": "An unexpected error occurred.", "code": "500"}), 500

@online_deduction_bp.route('/tasks/<string:task_uuid>/stop', methods=['POST'])
def stop_task_route(task_uuid: str):
    """
    Stop Running Task
    ---
    tags:
      - Online Deduction - Task Management
    parameters:
      - name: task_uuid
        in: path
        required: true
        description: Task UUID
        schema:
          type: string
    responses:
      200:
        description: Task stopped successfully
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
                    task_uuid: { type: string }
                    status: { type: string }
                    message: { type: string }
      400:
        description: Task cannot be stopped (not running)
      404:
        description: Task not found
      500:
        description: Internal server error
    """
    try:
        result, error = stop_task_service(task_uuid)

        if error:
            if "not found" in error.lower():
                return jsonify({"message": error, "code": "404"}), 404
            elif "not running" in error.lower():
                return jsonify({"message": error, "code": "400"}), 400
            
            current_app.logger.error(f"Error stopping task {task_uuid}: {error}")
            return jsonify({"message": f"Failed to stop task: {error}", "code": "500"}), 500
        
        return jsonify({"message": "success", "code": "200", "data": result}), 200

    except Exception as e:
        current_app.logger.error(f"Unexpected error in stop_task_route: {str(e)}")
        return jsonify({"message": "An unexpected error occurred.", "code": "500"}), 500 