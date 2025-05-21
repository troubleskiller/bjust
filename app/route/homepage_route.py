from flask import Blueprint, jsonify, current_app
from app.service.homepage_service import get_best_practice_cases_service

homepage_bp = Blueprint('homepage_bp', __name__, url_prefix='/api/v1/homepage')

@homepage_bp.route('/best_cases', methods=['GET'])
def get_best_practical_cases():
    """
    Get Best Practice Cases
    --- 
    tags:
      - Homepage
    responses:
      200:
        description: A list of best practice cases.
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
                      case_dir_name:
                        type: string
                        example: "case_folder_highway_scenario"
                      case_img:
                        type: string
                        example: "/storage/best_cases/case_folder_highway_scenario/thumbnail.jpg"
                      case_type:
                        type: string
                        example: "real_data"
                      case_title:
                        type: string
                        example: "高速公路场景信道特性分析"
                      model_name:
                        type: string
                        example: "Plana3.0,RayTracerX"
                      model_type_name:
                        type: string
                        example: "态势感知模型,大尺度模型"
                      create_date:
                        type: string
                        example: "2023-05-15"
      500:
        description: Internal server error.
    """
    try:
        cases, error = get_best_practice_cases_service()
        if error:
            current_app.logger.error(f"Error fetching best practice cases: {error}")
            return jsonify({"message": "Failed to retrieve best practice cases", "code": "500", "data": None}), 500
        
        return jsonify({"message": "success", "code": "200", "data": cases}), 200
    except Exception as e:
        current_app.logger.error(f"Exception in get_best_practical_cases: {str(e)}")
        return jsonify({"message": "An unexpected error occurred", "code": "500", "data": None}), 500 