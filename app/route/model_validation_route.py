from flask import Blueprint, jsonify, current_app, request
from app.service.model_validation_service import get_validation_task_types_service, get_validation_datasets_service, get_validation_models_service, create_validation_task_service

model_validation_bp = Blueprint('model_validation_bp', __name__, url_prefix='/api/v1/validation')

@model_validation_bp.route('/task_types', methods=['GET'])
def get_validation_task_types_route():
    """
    Get Validation Task Types
    ---
    tags:
      - Model Validation
    responses:
      200:
        description: A list of validation task types.
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
                      id:
                        type: string
                        example: "single_point_discrete"
                      name:
                        type: string
                        example: "单点预测-单点模式验证"
      500:
        description: Internal server error.
    """
    try:
        task_types, error = get_validation_task_types_service()
        if error:
            current_app.logger.error(f"Error fetching validation task types: {error}")
            return jsonify({"message": "Failed to retrieve validation task types", "code": "500", "data": None}), 500
        
        return jsonify({"message": "success", "code": "200", "data": task_types}), 200
    except Exception as e:
        current_app.logger.error(f"Exception in get_validation_task_types_route: {str(e)}")
        return jsonify({"message": "An unexpected error occurred", "code": "500", "data": None}), 500

@model_validation_bp.route('/datasets', methods=['GET'])
def get_validation_datasets_route():
    """
    Get Datasets for Validation
    ---
    tags:
      - Model Validation
    parameters:
      - name: task_type
        in: query
        required: true
        description: The ID of the validation task type (from /validation/task_types).
        schema:
          type: string
          example: "single_point_link"
    responses:
      200:
        description: A list of datasets suitable for the validation task type.
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
                      dataset_uuid:
                        type: string
                      dataset_name:
                        type: string
                      location_description:
                        type: string
                      center_frequency_mhz:
                        type: number
                        format: float
                      applicable_task_type:
                        type: string
      400:
        description: Missing or invalid task_type parameter.
      500:
        description: Internal server error.
    """
    task_type = request.args.get('task_type')
    if not task_type:
        return jsonify({"message": "task_type query parameter is required", "code": "400", "data": None}), 400

    try:
        datasets, error = get_validation_datasets_service(task_type)
        
        if error:
            # If service specifically said task_type is required but somehow it passed the route check.
            if "required" in error.lower(): 
                return jsonify({"message": error, "code": "400", "data": None}), 400
            current_app.logger.error(f"Error fetching validation datasets for task_type '{task_type}': {error}")
            return jsonify({"message": f"Failed to retrieve datasets: {error}", "code": "500", "data": None}), 500
        
        return jsonify({"message": "success", "code": "200", "data": datasets}), 200
    except Exception as e:
        current_app.logger.error(f"Exception in get_validation_datasets_route for task_type '{task_type}': {str(e)}")
        return jsonify({"message": "An unexpected error occurred", "code": "500", "data": None}), 500 

@model_validation_bp.route('/models', methods=['GET'])
def get_validation_models_route():
    """
    Get Models for Validation
    ---
    tags:
      - Model Validation
    parameters:
      - name: task_type
        in: query
        required: true
        description: The ID of the validation task type.
        schema:
          type: string
          example: "single_point_link"
      - name: dataset_uuid
        in: query
        required: true
        description: The UUID of the selected dataset.
        schema:
          type: string
    responses:
      200:
        description: A list of models suitable for the validation task and dataset.
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
                      model_name:
                        type: string
      400:
        description: Missing or invalid parameters, or dataset not suitable.
      404:
        description: Dataset not found.
      500:
        description: Internal server error.
    """
    task_type = request.args.get('task_type')
    dataset_uuid = request.args.get('dataset_uuid')

    if not task_type or not dataset_uuid:
        return jsonify({"message": "task_type and dataset_uuid query parameters are required", "code": "400", "data": None}), 400

    try:
        models, error = get_validation_models_service(task_type, dataset_uuid)

        if error:
            if "not found" in error.lower(): # Specifically for dataset not found
                return jsonify({"message": error, "code": "404", "data": None}), 404
            # For other logical errors from service (e.g., params required, dataset not suitable, invalid task type for matching)
            if "required" in error.lower() or "not suitable" in error.lower() or "Invalid validation task_type" in error.lower() :
                return jsonify({"message": error, "code": "400", "data": []}), 400 # Return empty list with specific error
            
            current_app.logger.error(f"Error fetching validation models (task: {task_type}, dataset: {dataset_uuid}): {error}")
            return jsonify({"message": f"Failed to retrieve models: {error}", "code": "500", "data": None}), 500
        
        # If models is None but no error, it implies a server-side issue not caught by service error message.
        if models is None:
            current_app.logger.error(f"Validation models service returned None data without error for task: {task_type}, dataset: {dataset_uuid}")
            return jsonify({"message": "Failed to retrieve models due to an unexpected issue.", "code": "500", "data": None}),500

        return jsonify({"message": "success", "code": "200", "data": models}), 200
    except Exception as e:
        current_app.logger.error(f"Exception in get_validation_models_route (task: {task_type}, dataset: {dataset_uuid}): {str(e)}")
        return jsonify({"message": "An unexpected error occurred", "code": "500", "data": None}), 500 

@model_validation_bp.route('/tasks', methods=['POST'])
def create_validation_task_route():
    """
    Create Model Validation Task
    ---
    tags:
      - Model Validation
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            required:
              - task_type
              - dataset_uuid
              - model_uuids
            properties:
              validation_task_name:
                type: string
                description: (Optional) User-defined name for the task.
              task_type:
                type: string
                description: Validation task type ID (from /validation/task_types).
              dataset_uuid:
                type: string
                description: UUID of the dataset to be used.
              model_uuids:
                type: array
                items:
                  type: string
                description: List of model UUIDs to compare.
              param_config:
                type: object
                description: (Optional) Parameters for small_scale tasks (e.g., modulation_mode, modulation_order).
                properties:
                  modulation_mode: { type: string }
                  modulation_order: { type: integer }
    responses:
      201:
        description: Validation task created successfully.
        content:
          application/json:
            schema:
              type: object
              properties:
                code: { type: string, example: "201" }
                message: { type: string, example: "Validation task created successfully." }
                data:
                  type: object
                  properties:
                    validation_task_uuid: { type: string }
      400:
        description: Bad request (e.g., missing fields, invalid UUIDs, unsuitable entities).
      404:
        description: Related entity (task type, dataset, model) not found.
      500:
        description: Internal server error.
    """
    if not request.is_json:
        return jsonify({"message": "Request must be JSON", "code": "400"}), 400

    data = request.get_json()
    if not data:
        return jsonify({"message": "No input data provided", "code": "400"}), 400

    try:
        result, error = create_validation_task_service(data)

        if error:
            if "not found" in error.lower():
                return jsonify({"message": error, "code": "404"}), 404
            # For missing fields, invalid list, unsuitable dataset/model etc.
            if "Missing required field" in error or \
               "must be a non-empty list" in error or \
               "Invalid task_type" in error or \
               "Dataset for validation must be" in error or \
               "not of a type suitable for task" in error: # Add more specific error checks if service returns them
                return jsonify({"message": error, "code": "400"}), 400
            
            current_app.logger.error(f"Error creating validation task: {error} (Data: {data})")
            return jsonify({"message": f"Failed to create validation task: {error}", "code": "500"}), 500
        
        return jsonify({"message": "Validation task created successfully.", "code": "201", "data": result}), 201

    except Exception as e:
        current_app.logger.error(f"Unexpected error in create_validation_task_route: {str(e)} (Data: {data})")
        return jsonify({"message": "An unexpected error occurred.", "code": "500"}), 500 