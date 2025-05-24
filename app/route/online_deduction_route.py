from flask import Blueprint, jsonify, current_app, request
from app.service.online_deduction_service import get_online_models_by_task_type_service, create_prediction_task_service, get_prediction_task_result_service

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
              point_config:
                type: object
                properties:
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
                    prediction_mode: { type: string }
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
    required_fields = ['model_uuid', 'prediction_mode', 'point_config', 'param_config']
    for field in required_fields:
        if field not in data:
            return jsonify({"message": f"Missing required field: {field}", "code": "400"}), 400

    try:
        result, error = create_prediction_task_service(data)

        if error:
            if "Invalid prediction_mode" in error or "Missing required field" in error or "Invalid" in error:
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