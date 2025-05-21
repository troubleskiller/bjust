from flask import Blueprint, jsonify, current_app, request
from app.service.model_plaza_service import (
    get_models_plaza_service, 
    get_grouped_models_service, 
    get_model_full_details_service,
    get_model_filter_options_service
)

model_plaza_bp = Blueprint('model_plaza_bp', __name__, url_prefix='/api/v1/models')

@model_plaza_bp.route('', methods=['GET'])
def get_models_route():
    """
    Get Model List for Model Plaza
    ---
    tags:
      - Model Plaza
    parameters:
      - name: page
        in: query
        required: false
        description: Page number, default 1.
        schema:
          type: integer
          default: 1
      - name: page_size
        in: query
        required: false
        description: Number of items per page, default 10.
        schema:
          type: integer
          default: 10
      - name: model_name_search
        in: query
        required: false
        description: Model name fuzzy search.
        schema:
          type: string
      - name: model_type
        in: query
        required: false
        description: Model type (e.g., "large_scale", "situation_awareness", "small_scale").
        schema:
          type: string
      - name: frequency_bands
        in: query
        required: false
        description: Comma-separated list of applicable frequency bands.
        schema:
          type: string
      - name: application_scenarios
        in: query
        required: false
        description: Comma-separated list of application scenarios.
        schema:
          type: string
    responses:
      200:
        description: A paginated list of models.
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
                  type: object
                  properties:
                    models:
                      type: array
                      items:
                        type: object
                        properties:
                          model_uuid:
                            type: string
                          model_name:
                            type: string
                          model_type:
                            type: string
                          frequency_bands:
                            type: array
                            items:
                              type: string
                          application_scenarios:
                            type: array
                            items:
                              type: string
                          update_time:
                            type: string
                            format: date-time
                          can_be_used_for_validation:
                            type: boolean
                    pagination:
                      type: object
                      properties:
                        current_page:
                          type: integer
                        page_size:
                          type: integer
                        total_items:
                          type: integer
                        total_pages:
                          type: integer
      400:
        description: Invalid query parameters.
      500:
        description: Internal server error.
    """
    try:
        page = request.args.get('page', default=1, type=int)
        page_size = request.args.get('page_size', default=10, type=int)
        model_name_search = request.args.get('model_name_search', default=None, type=str)
        model_type = request.args.get('model_type', default=None, type=str)
        frequency_bands_str = request.args.get('frequency_bands', default=None, type=str)
        application_scenarios_str = request.args.get('application_scenarios', default=None, type=str)

        if page < 1: page = 1
        if page_size < 1: page_size = 10
        if page_size > 100: page_size = 100 # Max page size limit

        models, pagination_info, error = get_models_plaza_service(
            page=page, 
            page_size=page_size, 
            model_name_search=model_name_search, 
            model_type=model_type, 
            frequency_bands_str=frequency_bands_str, 
            application_scenarios_str=application_scenarios_str
        )

        if error:
            current_app.logger.error(f"Error in get_models_route: {error}")
            return jsonify({"message": f"Failed to retrieve models: {error}", "code": "500", "data": None}), 500
        
        return jsonify({
            "message": "success", 
            "code": "200", 
            "data": {
                "models": models,
                "pagination": pagination_info
            }
        }), 200

    except ValueError as ve:
        current_app.logger.warning(f"Invalid parameter type in get_models_route: {str(ve)}")
        return jsonify({"message": f"Invalid parameter type: {str(ve)}", "code": "400", "data": None}), 400
    except Exception as e:
        current_app.logger.error(f"Unexpected exception in get_models_route: {str(e)}")
        return jsonify({"message": "An unexpected error occurred", "code": "500", "data": None}), 500

@model_plaza_bp.route('/grouped_list', methods=['GET'])
def get_grouped_models_route():
    """
    Get Grouped Model List for Model Detail Page Navigation
    ---
    tags:
      - Model Plaza
    responses:
      200:
        description: A list of models grouped by type.
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
                      group_name:
                        type: string
                        example: "大尺度模型"
                      group_id:
                        type: string
                        example: "large_scale"
                      models:
                        type: array
                        items:
                          type: object
                          properties:
                            model_uuid:
                              type: string
                            model_name:
                              type: string
      500:
        description: Internal server error.
    """
    try:
        grouped_models, error = get_grouped_models_service()

        if error:
            current_app.logger.error(f"Error in get_grouped_models_route: {error}")
            return jsonify({"message": f"Failed to retrieve grouped models: {error}", "code": "500", "data": None}), 500
        
        return jsonify({"message": "success", "code": "200", "data": grouped_models}), 200
    except Exception as e:
        current_app.logger.error(f"Unexpected exception in get_grouped_models_route: {str(e)}")
        return jsonify({"message": "An unexpected error occurred", "code": "500", "data": None}), 500

@model_plaza_bp.route('/filter_options', methods=['GET'])
def get_model_filter_options_route():
    """
    Get Model Filter Options for Model Plaza
    ---
    tags:
      - Model Plaza
    responses:
      200:
        description: A list of available filter options.
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
                  type: object
                  properties:
                    model_types:
                      type: array
                      items:
                        type: object
                        properties:
                          value: { type: string }
                          label: { type: string }
                    frequency_bands:
                      type: array
                      items:
                        type: object
                        properties:
                          value: { type: string }
                          label: { type: string }
                    application_scenarios:
                      type: array
                      items:
                        type: object
                        properties:
                          value: { type: string }
                          label: { type: string }
      500:
        description: Internal server error.
    """
    try:
        options, error = get_model_filter_options_service()

        if error:
            current_app.logger.error(f"Error in get_model_filter_options_route: {error}")
            return jsonify({"message": f"Failed to retrieve filter options: {error}", "code": "500", "data": None}), 500
        
        return jsonify({"message": "success", "code": "200", "data": options}), 200
    except Exception as e:
        current_app.logger.error(f"Unexpected exception in get_model_filter_options_route: {str(e)}")
        return jsonify({"message": "An unexpected error occurred", "code": "500", "data": None}), 500 