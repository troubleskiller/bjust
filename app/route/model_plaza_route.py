from flask import Blueprint, jsonify, current_app, request
from app.service.model_plaza_service import (
    get_models_plaza_service, 
    get_grouped_models_service, 
    get_model_full_details_service,
    get_model_filter_options_service,
    get_model_details_service,
    import_model_service,
    update_model_service,
    delete_model_service
)
from werkzeug.exceptions import RequestEntityTooLarge

model_plaza_bp = Blueprint('model_plaza_bp', __name__, url_prefix='/api/v1/models')

# Define allowed extensions for model files
ALLOWED_EXTENSIONS = {'zip'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

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

@model_plaza_bp.route('/<string:model_uuid>', methods=['GET'])
def get_model_details_route(model_uuid: str):
    """
    Get Model Details for Edit
    ---
    tags:
      - Model Plaza
    parameters:
      - name: model_uuid
        in: path
        required: true
        description: The UUID of the model.
        schema:
          type: string
    responses:
      200:
        description: Details of the specified model.
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
      404:
        description: Model not found.
      500:
        description: Internal server error.
    """
    try:
        details, error = get_model_details_service(model_uuid)

        if error:
            if "not found" in error.lower():
                return jsonify({"message": error, "code": "404", "data": None}), 404
            current_app.logger.error(f"Error fetching details for model {model_uuid}: {error}")
            return jsonify({"message": f"Failed to retrieve model details: {error}", "code": "500", "data": None}), 500
        
        if not details:
            return jsonify({"message": "Model not found.", "code": "404", "data": None}), 404

        return jsonify({"message": "success", "code": "200", "data": details}), 200
    except Exception as e:
        current_app.logger.error(f"Unexpected exception for model {model_uuid} details: {str(e)}")
        return jsonify({"message": "An unexpected error occurred", "code": "500", "data": None}), 500

@model_plaza_bp.route('', methods=['POST'])
def import_model_route():
    """
    Import/Create New Model
    ---
    tags:
      - Model Plaza
    requestBody:
      required: true
      content:
        multipart/form-data:
          schema:
            type: object
            required:
              - model_name
              - model_type
              - frequency_bands
              - application_scenarios
              - model_description
              - model_zip_file
            properties:
              model_name:
                type: string
                maxLength: 10
                description: Model name (up to 10 Chinese characters or equivalent)
              model_type:
                type: string
                enum: ["large_scale", "situation_awareness", "small_scale"]
              frequency_bands:
                type: string
                description: JSON string array of applicable frequency bands
              application_scenarios:
                type: string
                description: JSON string array of application scenarios
              model_description:
                type: string
                description: Model description
              model_zip_file:
                type: string
                format: binary
                description: ZIP file containing model, documentation, images, etc.
              dataset_for_validation_zip_file:
                type: string
                format: binary
                description: (Optional) ZIP file containing validation dataset
    responses:
      201:
        description: Model imported successfully.
        content:
          application/json:
            schema:
              type: object
              properties:
                code: { type: string, example: "201" }
                message: { type: string, example: "Model imported successfully." }
                data:
                  type: object
                  properties:
                    model_uuid: { type: string }
                    model_name: { type: string }
      400:
        description: Bad request (invalid data, missing fields, invalid file type).
      413:
        description: File too large.
      500:
        description: Internal server error.
    """
    if 'model_zip_file' not in request.files:
        return jsonify({"message": "No model_zip_file part in the request", "code": "400"}), 400
    
    model_file = request.files['model_zip_file']
    if model_file.filename == '':
        return jsonify({"message": "No model file selected", "code": "400"}), 400

    if not allowed_file(model_file.filename):
        return jsonify({"message": f"Invalid file type. Allowed types: {ALLOWED_EXTENSIONS}", "code": "400"}), 400

    # Optional validation dataset file
    validation_file = None
    if 'dataset_for_validation_zip_file' in request.files:
        validation_file = request.files['dataset_for_validation_zip_file']
        if validation_file.filename == '':
            validation_file = None
        elif not allowed_file(validation_file.filename):
            return jsonify({"message": f"Invalid validation file type. Allowed types: {ALLOWED_EXTENSIONS}", "code": "400"}), 400

    form_data = request.form.to_dict()

    try:
        # Basic validation
        required_fields = ['model_name', 'model_type', 'frequency_bands', 'application_scenarios', 'model_description']
        for field in required_fields:
            if field not in form_data or not form_data[field]:
                return jsonify({"message": f"Missing required field: {field}", "code": "400"}), 400

        # Validate model_name length (10 Chinese characters or equivalent)
        if len(form_data['model_name']) > 10:
            return jsonify({"message": "model_name cannot exceed 10 Chinese characters or equivalent.", "code": "400"}), 400

        # Validate model_type
        if form_data['model_type'] not in ["large_scale", "situation_awareness", "small_scale"]:
            return jsonify({"message": "Invalid model_type. Must be one of: large_scale, situation_awareness, small_scale", "code": "400"}), 400

        result, error = import_model_service(form_data, model_file, validation_file)

        if error:
            if "Missing required field" in error or \
               "Invalid data format" in error or \
               "Invalid file type" in error:
                return jsonify({"message": error, "code": "400"}), 400
            
            current_app.logger.error(f"Error importing model: {error}")
            return jsonify({"message": f"Failed to import model: {error}", "code": "500"}), 500
        
        return jsonify({"message": "Model imported successfully.", "code": "201", "data": result}), 201

    except RequestEntityTooLarge:
        return jsonify({"message": "File too large. Please ensure it is within the size limit.", "code": "413"}), 413
    except Exception as e:
        current_app.logger.error(f"Unexpected error in import_model_route: {str(e)}")
        return jsonify({"message": "An unexpected error occurred during import.", "code": "500"}), 500

@model_plaza_bp.route('/<string:model_uuid>', methods=['PUT'])
def update_model_route(model_uuid: str):
    """
    Update Model Information
    ---
    tags:
      - Model Plaza
    parameters:
      - name: model_uuid
        in: path
        required: true
        description: The UUID of the model to update.
        schema:
          type: string
    requestBody:
      content:
        application/json:
          schema:
            type: object
            properties:
              model_name: { type: string, maxLength: 10 }
              model_type: { type: string, enum: ["large_scale", "situation_awareness", "small_scale"] }
              frequency_bands: { type: array, items: { type: string } }
              application_scenarios: { type: array, items: { type: string } }
              model_description: { type: string }
        multipart/form-data:
          schema:
            type: object
            properties:
              model_name: { type: string, maxLength: 10 }
              model_type: { type: string, enum: ["large_scale", "situation_awareness", "small_scale"] }
              frequency_bands: { type: string, description: "JSON string array" }
              application_scenarios: { type: string, description: "JSON string array" }
              model_description: { type: string }
              model_zip_file: { type: string, format: binary }
              dataset_for_validation_zip_file: { type: string, format: binary }
    responses:
      200:
        description: Model updated successfully.
        content:
          application/json:
            schema:
              type: object
              properties:
                code: { type: string, example: "200" }
                message: { type: string, example: "Model updated successfully." }
                data: { type: object, properties: { model_uuid: { type: string } } }
      400:
        description: Bad request (invalid data, invalid file type).
      404:
        description: Model not found.
      413:
        description: File too large.
      415:
        description: Unsupported Content-Type.
      500:
        description: Internal server error.
    """
    update_data = {}
    model_file = None
    validation_file = None

    if request.content_type and request.content_type.startswith('multipart/form-data'):
        update_data = request.form.to_dict()
        
        if 'model_zip_file' in request.files:
            model_file = request.files['model_zip_file']
            if model_file.filename == '':
                model_file = None
            elif not allowed_file(model_file.filename):
                return jsonify({"message": f"Invalid model file type. Allowed types: {ALLOWED_EXTENSIONS}", "code": "400"}), 400
        
        if 'dataset_for_validation_zip_file' in request.files:
            validation_file = request.files['dataset_for_validation_zip_file']
            if validation_file.filename == '':
                validation_file = None
            elif not allowed_file(validation_file.filename):
                return jsonify({"message": f"Invalid validation file type. Allowed types: {ALLOWED_EXTENSIONS}", "code": "400"}), 400
                
    elif request.content_type and request.content_type.startswith('application/json'):
        update_data = request.json
        if not update_data:
            update_data = {}
    else:
        return jsonify({"message": "Unsupported Content-Type. Use application/json or multipart/form-data.", "code": "415"}), 415

    # Basic validations
    try:
        if 'model_name' in update_data and update_data['model_name'] is not None and len(update_data['model_name']) > 10:
            return jsonify({"message": "model_name cannot exceed 10 Chinese characters or equivalent.", "code": "400"}), 400
        if 'model_type' in update_data and update_data['model_type'] is not None and update_data['model_type'] not in ["large_scale", "situation_awareness", "small_scale"]:
            return jsonify({"message": "Invalid model_type. Must be one of: large_scale, situation_awareness, small_scale", "code": "400"}), 400

    except (ValueError, TypeError) as ve:
        return jsonify({"message": f"Invalid format for a field: {str(ve)}", "code": "400"}), 400

    if not update_data and not model_file and not validation_file:
        return jsonify({"message": "No update data or files provided.", "code": "400"}), 400

    try:
        result, error = update_model_service(model_uuid, update_data, model_file, validation_file)

        if error:
            if "not found" in error.lower():
                return jsonify({"message": error, "code": "404"}), 404
            if "Invalid data format" in error:
                return jsonify({"message": error, "code": "400"}), 400
            current_app.logger.error(f"Error updating model {model_uuid}: {error}")
            return jsonify({"message": f"Failed to update model: {error}", "code": "500"}), 500
        
        return jsonify({"message": "Model updated successfully.", "code": "200", "data": result}), 200

    except RequestEntityTooLarge:
        return jsonify({"message": "File too large.", "code": "413"}), 413
    except Exception as e:
        current_app.logger.error(f"Unexpected error updating model {model_uuid}: {str(e)}")
        return jsonify({"message": "An unexpected error occurred during update.", "code": "500"}), 500

@model_plaza_bp.route('/<string:model_uuid>', methods=['DELETE'])
def delete_model_route(model_uuid: str):
    """
    Delete Model
    ---
    tags:
      - Model Plaza
    parameters:
      - name: model_uuid
        in: path
        required: true
        description: The UUID of the model to delete.
        schema:
          type: string
    responses:
      200:
        description: Model deleted successfully.
        content:
          application/json:
            schema:
              type: object
              properties:
                code: { type: string, example: "200" }
                message: { type: string, example: "Model deleted successfully." }
                data: { type: 'null' }
      404:
        description: Model not found.
      500:
        description: Internal server error.
    """
    try:
        success, error = delete_model_service(model_uuid)

        if not success and error == "Model not found.":
            return jsonify({"message": error, "code": "404", "data": None}), 404
        
        if error:
            current_app.logger.error(f"Error deleting model {model_uuid}: {error}")
            return jsonify({"message": f"Failed to delete model: {error}", "code": "500", "data": None}), 500
        
        return jsonify({"message": "Model deleted successfully.", "code": "200", "data": None}), 200

    except Exception as e:
        current_app.logger.error(f"Unexpected error deleting model {model_uuid}: {str(e)}")
        return jsonify({"message": "An unexpected error occurred during deletion.", "code": "500", "data": None}), 500

@model_plaza_bp.route('/<string:model_uuid>/details', methods=['GET'])
def get_model_full_details_route(model_uuid: str):
    """
    Get Model Full Details for Detail Page
    ---
    tags:
      - Model Detail Introduction
    parameters:
      - name: model_uuid
        in: path
        required: true
        description: The UUID of the model.
        schema:
          type: string
    responses:
      200:
        description: Full details of the specified model.
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
      404:
        description: Model not found.
      500:
        description: Internal server error.
    """
    try:
        details, error = get_model_full_details_service(model_uuid)

        if error:
            if "not found" in error.lower():
                return jsonify({"message": error, "code": "404", "data": None}), 404
            current_app.logger.error(f"Error fetching full details for model {model_uuid}: {error}")
            return jsonify({"message": f"Failed to retrieve model details: {error}", "code": "500", "data": None}), 500
        
        if not details:
            return jsonify({"message": "Model not found.", "code": "404", "data": None}), 404

        return jsonify({"message": "success", "code": "200", "data": details}), 200
    except Exception as e:
        current_app.logger.error(f"Unexpected exception for model {model_uuid} full details: {str(e)}")
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