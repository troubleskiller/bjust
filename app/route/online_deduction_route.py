from flask import Blueprint, jsonify, current_app, request
from app.service.online_deduction_service import get_online_models_by_task_type_service

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