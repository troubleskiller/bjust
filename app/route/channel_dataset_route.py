from flask import Blueprint, jsonify, current_app, request, send_from_directory
from app.service.channel_dataset_service import get_channel_datasets_service, get_dataset_upload_template_path_service, get_channel_dataset_details_service, import_channel_dataset_service, update_channel_dataset_service, delete_channel_dataset_service
import os
from werkzeug.exceptions import RequestEntityTooLarge

channel_dataset_bp = Blueprint('channel_dataset_bp', __name__, url_prefix='/api/v1/channel_datasets')

@channel_dataset_bp.route('', methods=['GET'])
def get_channel_datasets_route():
    """
    Get Channel Dataset List
    ---
    tags:
      - Channel Data Management
    parameters:
      - name: page
        in: query
        type: integer
        required: false
        description: Page number.
      - name: page_size
        in: query
        type: integer
        required: false
        description: Number of items per page.
      - name: dataset_name_search
        in: query
        type: string
        required: false
        description: Dataset name fuzzy search.
      - name: data_type
        in: query
        type: string
        required: false
        description: Data type ("real_measurement", "simulation").
      - name: location_description_search
        in: query
        type: string
        required: false
        description: Location description fuzzy search.
      - name: center_frequency_mhz
        in: query
        type: number
        format: float
        required: false
        description: Center frequency in MHz.
      - name: applicable_task_type
        in: query
        type: string
        required: false
        description: Applicable task type (e.g., "single_point_prediction").
    responses:
      200:
        description: A paginated list of channel datasets.
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
                    datasets:
                      type: array
                      items:
                        # Refer to task.md for dataset item structure
                        type: object 
                    pagination:
                      type: object
                      # Refer to task.md for pagination structure
      400:
        description: Invalid query parameters.
      500:
        description: Internal server error.
    """
    try:
        page = request.args.get('page', default=1, type=int)
        page_size = request.args.get('page_size', default=10, type=int)
        dataset_name_search = request.args.get('dataset_name_search', type=str)
        data_type = request.args.get('data_type', type=str)
        location_description_search = request.args.get('location_description_search', type=str)
        center_frequency_mhz_str = request.args.get('center_frequency_mhz', type=str) # get as str first
        applicable_task_type = request.args.get('applicable_task_type', type=str)

        center_frequency_mhz = None
        if center_frequency_mhz_str:
            try:
                center_frequency_mhz = float(center_frequency_mhz_str)
            except ValueError:
                return jsonify({"message": "Invalid format for center_frequency_mhz. Must be a number.", "code": "400", "data": None}), 400

        if page < 1: page = 1
        if page_size < 1: page_size = 10
        if page_size > 100: page_size = 100 # Max page size

        datasets, pagination_info, error = get_channel_datasets_service(
            page=page, page_size=page_size,
            dataset_name_search=dataset_name_search,
            data_type=data_type,
            location_description_search=location_description_search,
            center_frequency_mhz=center_frequency_mhz,
            applicable_task_type=applicable_task_type
        )

        if error:
            # Check if the error message from service indicates a user input error (like invalid format)
            if "Invalid" in error or "format" in error: 
                 return jsonify({"message": error, "code": "400", "data": None}), 400
            current_app.logger.error(f"Error in get_channel_datasets_route: {error}")
            return jsonify({"message": f"Failed to retrieve datasets: {error}", "code": "500", "data": None}), 500
        
        return jsonify({
            "message": "success", 
            "code": "200", 
            "data": {
                "datasets": datasets,
                "pagination": pagination_info
            }
        }), 200

    except ValueError as ve: # Catch type conversion errors from request.args.get if any
        current_app.logger.warning(f"Invalid parameter type in get_channel_datasets_route: {str(ve)}")
        return jsonify({"message": f"Invalid parameter type: {str(ve)}", "code": "400", "data": None}), 400
    except Exception as e:
        current_app.logger.error(f"Unexpected exception in get_channel_datasets_route: {str(e)}")
        return jsonify({"message": "An unexpected error occurred", "code": "500", "data": None}), 500 

@channel_dataset_bp.route('/upload_template', methods=['GET'])
def get_dataset_upload_template_route():
    """
    Download Dataset Upload Template
    ---
    tags:
      - Channel Data Management
    parameters:
      - name: task_type
        in: query
        type: string
        required: false
        description: Specific task type for the template (e.g., "single_point_prediction_link_mode").
    responses:
      200:
        description: Excel template file.
        content:
          application/vnd.ms-excel:
            schema:
              type: string
              format: binary
          application/vnd.openxmlformats-officedocument.spreadsheetml.sheet:
            schema:
              type: string
              format: binary
      400:
        description: Invalid task_type or template not found for the type.
      404:
        description: Template file not found.
      500:
        description: Internal server error.
    """
    task_type = request.args.get('task_type', type=str, default=None)

    try:
        template_dir, template_filename, error = get_dataset_upload_template_path_service(task_type)

        if error:
            # Distinguish between client error (bad task_type, specific template missing) vs server error (dir misconfig)
            if "not found" in error.lower() or "Invalid" in error.lower():
                if "directory not found" in error.lower() or "not configured" in error.lower(): # Server-side issue
                    current_app.logger.error(f"Template directory misconfiguration: {error}")
                    return jsonify({"message": "Template directory error.", "code": "500"}), 500
                # Client-side, specific template for task type not found
                return jsonify({"message": error, "code": "404"}), 404 # Or 400 if task_type was invalid
            current_app.logger.error(f"Error getting template path: {error}")
            return jsonify({"message": "Error finding template.", "code": "500"}), 500

        if not template_dir or not template_filename:
            # This case should ideally be caught by the error handling above
            current_app.logger.error("Template directory or filename not determined by service.")
            return jsonify({"message": "Could not determine template file.", "code": "500"}), 500

        return send_from_directory(template_dir, template_filename, as_attachment=True)
    
    except Exception as e:
        current_app.logger.error(f"Unexpected error in get_dataset_upload_template_route: {str(e)}")
        return jsonify({"message": "An unexpected server error occurred.", "code": "500"}), 500 

@channel_dataset_bp.route('/<string:dataset_uuid>', methods=['GET'])
def get_channel_dataset_details_route(dataset_uuid: str):
    """
    Get Channel Dataset Details for Edit
    ---
    tags:
      - Channel Data Management
    parameters:
      - name: dataset_uuid
        in: path
        required: true
        description: The UUID of the dataset.
        schema:
          type: string
    responses:
      200:
        description: Details of the specified channel dataset.
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
                  # Refer to task.md for the detailed structure of dataset details
                  type: object
      404:
        description: Dataset not found.
      500:
        description: Internal server error.
    """
    try:
        details, error = get_channel_dataset_details_service(dataset_uuid)

        if error:
            if "not found" in error.lower():
                return jsonify({"message": error, "code": "404", "data": None}), 404
            current_app.logger.error(f"Error fetching details for dataset {dataset_uuid}: {error}")
            return jsonify({"message": f"Failed to retrieve dataset details: {error}", "code": "500", "data": None}), 500
        
        if not details: # Should be caught by the error if dataset not found
            return jsonify({"message": "Dataset not found.", "code": "404", "data": None}), 404

        return jsonify({"message": "success", "code": "200", "data": details}), 200
    except Exception as e:
        current_app.logger.error(f"Unexpected exception for dataset {dataset_uuid} details: {str(e)}")
        return jsonify({"message": "An unexpected error occurred", "code": "500", "data": None}), 500

# Placeholder for the actual file download route mentioned in the service
@channel_dataset_bp.route('/<string:dataset_uuid>/download', methods=['GET'])
def download_channel_dataset_file_route(dataset_uuid: str):
    """
    Download Channel Dataset File (Actual implementation needed)
    ---
    tags:
      - Channel Data Management
    parameters:
      - name: dataset_uuid
        in: path
        required: true
        description: The UUID of the dataset to download.
        schema:
          type: string
    responses:
      200:
        description: The dataset file.
        # content types will vary based on file
      404:
        description: Dataset or file not found.
      500:
        description: Internal server error.
    """
    # TODO: Implement the actual file download logic
    # 1. Fetch dataset record by dataset_uuid to get dataset_file_storage_path
    # 2. Construct full path to the file using a base storage directory (e.g., current_app.config['DATASET_STORAGE_DIR'])
    # 3. Use send_from_directory to send the file.
    # Ensure proper error handling if dataset or file not found.
    dataset = ChannelDataset.query.filter(ChannelDataset.dataset_uuid == dataset_uuid).first()
    if not dataset or not dataset.dataset_file_storage_path:
        return jsonify({"message": "Dataset file not found or path not specified.", "code": "404"}), 404

    try:
        # It's good practice to have a dedicated, configurable directory for dataset storage
        dataset_storage_dir = current_app.config.get('DATASET_FILES_DIR')
        if not dataset_storage_dir:
            # Fallback to a default, ensure this is correctly configured
            dataset_storage_dir = os.path.join(current_app.config.get('STORAGE_FOLDER', 'storage'), 'channel_datasets_files')
            
        # dataset.dataset_file_storage_path should be the filename if files are stored in dataset_storage_dir directly
        # Or it could be a relative path within dataset_storage_dir
        # For send_from_directory, the first arg is directory, second is filename relative to that directory.
        # Assuming dataset_file_storage_path is just the filename here:
        filename = dataset.file_name_original # Or derive from dataset_file_storage_path if it's just the name
        # If dataset_file_storage_path contains subdirectories, adjust accordingly.

        # For safety, it's better if dataset_file_storage_path is just the filename, and not a full or relative path
        # that could be manipulated for directory traversal if it came from user input (though here it's from DB).
        # Securely get the filename from dataset_file_storage_path if it's a full path:
        # secure_filename = os.path.basename(dataset.dataset_file_storage_path)
        
        # Assuming dataset_file_storage_path stores the filename and files are in dataset_storage_dir
        if not os.path.isfile(os.path.join(dataset_storage_dir, filename)):
             return jsonify({"message": f"File {filename} not found in storage directory.", "code": "404"}), 404

        return send_from_directory(dataset_storage_dir, filename, as_attachment=True)
    except Exception as e:
        current_app.logger.error(f"Error downloading dataset file for {dataset_uuid}: {str(e)}")
        return jsonify({"message": "Error during file download.", "code": "500"}), 500 

# Define allowed extensions for dataset files for basic validation
ALLOWED_EXTENSIONS = {'zip', 'xls', 'xlsx'} # As per task.md "ZIP或Excel"

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@channel_dataset_bp.route('', methods=['POST'])
def import_channel_dataset_route():
    """
    Import Channel Dataset
    ---
    tags:
      - Channel Data Management
    requestBody:
      required: true
      content:
        multipart/form-data:
          schema:
            type: object
            required:
              - dataset_name
              - data_type
              - location_description
              - center_frequency_mhz
              - bandwidth_mhz
              - data_volume_groups
              - applicable_task_type
              - dataset_file
            properties:
              dataset_name: { type: string, maxLength: 25 }
              data_type: { type: string, enum: ["real_measurement", "simulation"] }
              location_description: { type: string }
              center_frequency_mhz: { type: number, format: float }
              bandwidth_mhz: { type: number, format: float }
              data_volume_groups: { type: integer }
              applicable_task_type: { type: string }
              dataset_file: { type: string, format: binary }
    responses:
      201:
        description: Dataset imported successfully.
        content:
          application/json:
            schema:
              type: object
              properties:
                code: { type: string, example: "201" }
                message: { type: string, example: "Dataset imported successfully." }
                data: 
                  type: object
                  properties:
                    dataset_uuid: { type: string }
                    dataset_name: { type: string }
      400:
        description: Bad request (e.g., missing fields, invalid data, invalid file type, file too large).
      500:
        description: Internal server error.
    """
    if 'dataset_file' not in request.files:
        return jsonify({"message": "No dataset_file part in the request", "code": "400"}), 400
    
    file = request.files['dataset_file']
    if file.filename == '':
        return jsonify({"message": "No selected file", "code": "400"}), 400

    if not allowed_file(file.filename):
        return jsonify({"message": f"Invalid file type. Allowed types: {ALLOWED_EXTENSIONS}", "code": "400"}), 400

    form_data = request.form.to_dict()

    try:
        # Basic validation for dataset_name length
        if 'dataset_name' in form_data and len(form_data['dataset_name']) > 25:
             return jsonify({"message": "dataset_name cannot exceed 25 characters.", "code": "400"}), 400
        # Add more specific validations as needed for other fields based on task.md constraints
        # e.g., data_type enum check (though service might also do this)
        if 'data_type' in form_data and form_data['data_type'] not in ["real_measurement", "simulation"]:
            return jsonify({"message": "Invalid data_type. Must be 'real_measurement' or 'simulation'.", "code": "400"}), 400

        # Attempt to convert numeric fields early to catch format errors before service call
        try:
            form_data['center_frequency_mhz'] = float(form_data.get('center_frequency_mhz'))
            form_data['bandwidth_mhz'] = float(form_data.get('bandwidth_mhz'))
            form_data['data_volume_groups'] = int(form_data.get('data_volume_groups'))
        except (ValueError, TypeError) as ve:
            return jsonify({"message": f"Invalid format for numeric field: {str(ve)}", "code": "400"}), 400

        result, error = import_channel_dataset_service(form_data, file)

        if error:
            # Check for user-facing errors vs server errors
            if "Missing required field" in error or \
               "Invalid data format" in error or \
               "File storage directory not configured" in error or \
               "Invalid file type" in error:
                return jsonify({"message": error, "code": "400"}), 400
            
            current_app.logger.error(f"Error importing dataset: {error}")
            return jsonify({"message": f"Failed to import dataset: {error}", "code": "500"}), 500
        
        return jsonify({"message": "Dataset imported successfully.", "code": "201", "data": result}), 201

    except RequestEntityTooLarge:
        return jsonify({"message": "File too large. Please ensure it is within the size limit.", "code": "413"}), 413
    except Exception as e:
        current_app.logger.error(f"Unexpected error in import_channel_dataset_route: {str(e)}")
        return jsonify({"message": "An unexpected error occurred during import.", "code": "500"}), 500 

@channel_dataset_bp.route('/<string:dataset_uuid>', methods=['PUT'])
def update_channel_dataset_route(dataset_uuid: str):
    """
    Update Channel Dataset Metadata (and optionally file)
    ---
    tags:
      - Channel Data Management
    parameters:
      - name: dataset_uuid
        in: path
        required: true
        description: The UUID of the dataset to update.
        schema:
          type: string
    requestBody:
      content:
        application/json:
          schema:
            type: object
            # All fields are optional for update
            properties:
              dataset_name: { type: string, maxLength: 25 }
              data_type: { type: string, enum: ["real_measurement", "simulation"] }
              location_description: { type: string }
              center_frequency_mhz: { type: number, format: float, nullable: true }
              bandwidth_mhz: { type: number, format: float, nullable: true }
              data_volume_groups: { type: integer, nullable: true }
              applicable_task_type: { type: string, nullable: true }
        multipart/form-data:
          schema:
            type: object
            properties:
              # Same as JSON, but with dataset_file
              dataset_name: { type: string, maxLength: 25 }
              data_type: { type: string, enum: ["real_measurement", "simulation"] }
              location_description: { type: string }
              center_frequency_mhz: { type: number, format: float, nullable: true }
              bandwidth_mhz: { type: number, format: float, nullable: true }
              data_volume_groups: { type: integer, nullable: true }
              applicable_task_type: { type: string, nullable: true }
              dataset_file: { type: string, format: binary, nullable: true }
    responses:
      200:
        description: Dataset updated successfully.
        content:
          application/json:
            schema:
              type: object
              properties:
                code: { type: string, example: "200" }
                message: { type: string, example: "Dataset updated successfully." }
                data: { type: object, properties: { dataset_uuid: { type: string } } }
      400:
        description: Bad request (e.g., invalid data, invalid file type).
      404:
        description: Dataset not found.
      413:
        description: File too large.
      500:
        description: Internal server error.
    """
    update_data = {}
    new_file = None

    if request.content_type.startswith('multipart/form-data'):
        update_data = request.form.to_dict()
        if 'dataset_file' in request.files:
            new_file = request.files['dataset_file']
            if new_file.filename == '': # No file selected, but field was present
                new_file = None 
            elif not allowed_file(new_file.filename):
                 return jsonify({"message": f"Invalid file type. Allowed types: {ALLOWED_EXTENSIONS}", "code": "400"}), 400
    elif request.content_type.startswith('application/json'):
        update_data = request.json
        if not update_data: # Ensure request.json is not None for empty JSON body {} case
            update_data = {}
    else:
        return jsonify({"message": "Unsupported Content-Type. Use application/json or multipart/form-data.", "code": "415"}), 415

    # Type conversions and basic validations
    try:
        if 'dataset_name' in update_data and update_data['dataset_name'] is not None and len(update_data['dataset_name']) > 25:
            return jsonify({"message": "dataset_name cannot exceed 25 characters.", "code": "400"}), 400
        if 'data_type' in update_data and update_data['data_type'] is not None and update_data['data_type'] not in ["real_measurement", "simulation"]:
            return jsonify({"message": "Invalid data_type. Must be 'real_measurement' or 'simulation'.", "code": "400"}), 400
        
        # Ensure numeric fields are correctly typed if present
        for field in ['center_frequency_mhz', 'bandwidth_mhz']:
            if field in update_data and update_data[field] is not None:
                update_data[field] = float(update_data[field])
        if 'data_volume_groups' in update_data and update_data['data_volume_groups'] is not None:
            update_data[field] = int(update_data[field])

    except (ValueError, TypeError) as ve:
        return jsonify({"message": f"Invalid format for a field: {str(ve)}", "code": "400"}), 400

    if not update_data and not new_file:
        return jsonify({"message": "No update data or file provided.", "code": "400"}), 400

    try:
        result, error = update_channel_dataset_service(dataset_uuid, update_data, new_file)

        if error:
            if "not found" in error.lower():
                return jsonify({"message": error, "code": "404"}), 404
            if "Invalid data format" in error or "File storage directory not configured" in error:
                 return jsonify({"message": error, "code": "400"}), 400 # Could also be 500 for config error
            current_app.logger.error(f"Error updating dataset {dataset_uuid}: {error}")
            return jsonify({"message": f"Failed to update dataset: {error}", "code": "500"}), 500
        
        return jsonify({"message": "Dataset updated successfully.", "code": "200", "data": result}), 200

    except RequestEntityTooLarge:
        return jsonify({"message": "File too large.", "code": "413"}), 413
    except Exception as e:
        current_app.logger.error(f"Unexpected error updating dataset {dataset_uuid}: {str(e)}")
        return jsonify({"message": "An unexpected error occurred during update.", "code": "500"}), 500 

@channel_dataset_bp.route('/<string:dataset_uuid>', methods=['DELETE'])
def delete_channel_dataset_route(dataset_uuid: str):
    """
    Delete Channel Dataset
    ---
    tags:
      - Channel Data Management
    parameters:
      - name: dataset_uuid
        in: path
        required: true
        description: The UUID of the dataset to delete.
        schema:
          type: string
    responses:
      200:
        description: Dataset deleted successfully.
        content:
          application/json:
            schema:
              type: object
              properties:
                code: { type: string, example: "200" }
                message: { type: string, example: "Dataset deleted successfully." }
                data: { type: 'null' }
      # Per task.md, can also be 204 No Content. 
      # For consistency with other APIs, using 200 with a body.
      # To use 204: return '', 204
      404:
        description: Dataset not found.
      500:
        description: Internal server error.
    """
    try:
        success, error = delete_channel_dataset_service(dataset_uuid)

        if not success and error == "Dataset not found.":
            return jsonify({"message": error, "code": "404", "data": None}), 404
        
        if error:
            current_app.logger.error(f"Error deleting dataset {dataset_uuid}: {error}")
            return jsonify({"message": f"Failed to delete dataset: {error}", "code": "500", "data": None}), 500
        
        # If success is True, error should be None
        return jsonify({"message": "Dataset deleted successfully.", "code": "200", "data": None}), 200

    except Exception as e:
        current_app.logger.error(f"Unexpected error deleting dataset {dataset_uuid}: {str(e)}")
        return jsonify({"message": "An unexpected error occurred during deletion.", "code": "500", "data": None}), 500 