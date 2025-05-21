from flask import current_app
import os
from app.model.dataset_info import ChannelDataset
from flask import url_for
from app import db # Assuming db is your SQLAlchemy instance
from werkzeug.utils import secure_filename
import uuid # For generating dataset_uuid
import datetime

def get_channel_datasets_service():
    """
    Placeholder for get_channel_datasets_service.
    Implement actual logic as needed.
    """
    # TODO: Implement actual logic to fetch channel datasets
    print("get_channel_datasets_service called - placeholder")
    return [], None # Example: return empty list and no error

DEFAULT_TEMPLATE_FILENAME = "default_dataset_template.xlsx"
TASK_TYPE_TEMPLATE_MAPPING = {
    "single_point_prediction_discrete_mode": "single_point_discrete_template.xlsx",
    "single_point_prediction_link_mode": "single_point_link_template.xlsx",
    "situation_prediction": "situation_template.xlsx",
    "small_scale_prediction": "small_scale_template.xlsx",
    # Add other mappings as needed
}

def get_dataset_upload_template_path_service(task_type: str = None):
    """
    Determines the path to the dataset upload template file.
    Returns the directory path and the filename.
    """
    try:
        # It's good practice to have a dedicated, configurable directory for templates
        template_dir = current_app.config.get('DATASET_TEMPLATE_DIR')
        if not template_dir:
            # Fallback to a default location if not configured
            # Ensure this path is correct relative to your app's instance or root path
            template_dir = os.path.join(current_app.root_path, '..' , 'storage', 'dataset_templates')
            # For a typical app structure where app is a package and storage is sibling to app:
            # template_dir = os.path.abspath(os.path.join(current_app.root_path, '..', 'storage', 'dataset_templates'))

        if not os.path.isdir(template_dir):
            return None, None, f"Template directory not found or not configured: {template_dir}"

        template_filename = DEFAULT_TEMPLATE_FILENAME
        if task_type and task_type in TASK_TYPE_TEMPLATE_MAPPING:
            template_filename = TASK_TYPE_TEMPLATE_MAPPING[task_type]
        
        full_path = os.path.join(template_dir, template_filename)
        if not os.path.isfile(full_path):
            # If specific template not found, try falling back to default if not already chosen
            if template_filename != DEFAULT_TEMPLATE_FILENAME:
                default_full_path = os.path.join(template_dir, DEFAULT_TEMPLATE_FILENAME)
                if os.path.isfile(default_full_path):
                    return template_dir, DEFAULT_TEMPLATE_FILENAME, None # Return dir and filename
            return None, None, f"Template file '{template_filename}' not found in {template_dir}."
            
        return template_dir, template_filename, None # Return dir and filename

    except Exception as e:
        # current_app.logger.error(f"Error in get_dataset_upload_template_path_service: {str(e)}")
        return None, None, str(e) 

def get_channel_dataset_details_service(dataset_uuid: str):
    """
    Service to fetch details for a specific channel dataset.
    """
    try:
        dataset = ChannelDataset.query.filter(ChannelDataset.dataset_uuid == dataset_uuid).first()
        
        if not dataset:
            return None, "Dataset not found."
        
        # Prepare data for the response, matching the API doc structure
        dataset_details_data = {
            "dataset_uuid": dataset.dataset_uuid,
            "dataset_name": dataset.dataset_name,
            "data_type": dataset.data_type,
            "location_description": dataset.location_description,
            "center_frequency_mhz": dataset.center_frequency_mhz,
            "bandwidth_mhz": dataset.bandwidth_mhz,
            "data_volume_groups": dataset.data_volume_groups,
            "applicable_task_type": dataset.applicable_task_type,
            "update_time": dataset.updated_at.isoformat() + "Z",
            "file_name": dataset.file_name_original,
            # Generate file_download_url. This requires a route to handle the download.
            # Assuming a route like '/api/v1/channel_datasets/<dataset_uuid>/download' will be created.
            # If a direct storage URL is available and preferred, that logic would go here.
            "file_download_url": url_for('channel_dataset_bp.download_channel_dataset_file_route', 
                                           dataset_uuid=dataset.dataset_uuid, _external=True)
        }
        return dataset_details_data, None
    except Exception as e:
        # current_app.logger.error(f"Error in get_channel_dataset_details_service for {dataset_uuid}: {str(e)}")
        return None, str(e) 

def generate_new_dataset_uuid():
    """Generates a new unique UUID for a dataset."""
    return f"ds-uuid-{uuid.uuid4().hex}"

def import_channel_dataset_service(form_data, file_storage):
    """
    Service to import a new channel dataset.
    Handles file saving and database record creation.
    form_data: dict containing the non-file form fields.
    file_storage: FileStorage object for 'dataset_file'.
    """
    try:
        # 1. Validate required fields (as per task.md)
        required_fields = [
            'dataset_name', 'data_type', 'location_description',
            'center_frequency_mhz', 'bandwidth_mhz', 'data_volume_groups',
            'applicable_task_type'
        ]
        for field in required_fields:
            if field not in form_data or not form_data[field]:
                return None, f"Missing required field: {field}"
        
        if not file_storage:
            return None, "Missing dataset_file."

        # 2. Secure and save the uploaded file
        original_filename = secure_filename(file_storage.filename)
        # Generate a new unique filename for storage to avoid conflicts, or use a subfolder per dataset_uuid
        # For now, let's assume a flat storage structure with unique filenames (e.g., prefix with dataset_uuid)
        # This needs to be coordinated with how files are retrieved by download_channel_dataset_file_route
        
        dataset_uuid_val = generate_new_dataset_uuid()
        # Example: stored_filename = f"{dataset_uuid_val}_{original_filename}"
        # However, the download route currently uses file_name_original. 
        # Let's stick to storing original_filename and ensure DATASET_FILES_DIR is well-managed or use subdirectories.
        # For simplicity now, we save with original_filename. If duplicates are an issue, a more robust strategy is needed.
        stored_filename = original_filename 

        dataset_storage_dir = current_app.config.get('DATASET_FILES_DIR')
        if not dataset_storage_dir:
            # Fallback or error, ensure this is configured
            # current_app.logger.error("DATASET_FILES_DIR not configured.")
            return None, "File storage directory not configured."
        
        if not os.path.exists(dataset_storage_dir):
            os.makedirs(dataset_storage_dir, exist_ok=True)
            
        file_path = os.path.join(dataset_storage_dir, stored_filename)
        
        # Check for potential filename collision if not using UUIDs in filenames
        if os.path.exists(file_path):
            # Simple collision handling: append a UUID or timestamp part to filename
            name_part, ext_part = os.path.splitext(stored_filename)
            stored_filename = f"{name_part}_{uuid.uuid4().hex[:8]}{ext_part}"
            file_path = os.path.join(dataset_storage_dir, stored_filename)

        file_storage.save(file_path)

        # 3. Create and save the database record
        new_dataset = ChannelDataset(
            dataset_uuid=dataset_uuid_val,
            dataset_name=form_data['dataset_name'],
            data_type=form_data['data_type'],
            location_description=form_data['location_description'],
            center_frequency_mhz=float(form_data['center_frequency_mhz']),
            bandwidth_mhz=float(form_data['bandwidth_mhz']),
            data_volume_groups=int(form_data['data_volume_groups']),
            applicable_task_type=form_data['applicable_task_type'],
            file_name_original=original_filename, # Store the original name for display/download
            dataset_file_storage_path=stored_filename # This path is relative to DATASET_FILES_DIR or how download route interprets it
                                                    # If download route uses file_name_original, this could be just stored_filename
        )
        
        db.session.add(new_dataset)
        db.session.commit()
        
        return {"dataset_uuid": new_dataset.dataset_uuid, "dataset_name": new_dataset.dataset_name}, None

    except ValueError as ve:
        # db.session.rollback() # Rollback in case of partial commit or other issues
        return None, f"Invalid data format for numeric fields: {str(ve)}"
    except Exception as e:
        db.session.rollback()
        # current_app.logger.error(f"Error in import_channel_dataset_service: {str(e)}")
        # Potentially remove the saved file if DB commit fails
        # if 'file_path' in locals() and os.path.exists(file_path):
        #     os.remove(file_path)
        return None, str(e) 

def update_channel_dataset_service(dataset_uuid: str, update_data: dict, new_file_storage=None):
    """
    Service to update an existing channel dataset's metadata and optionally its file.
    update_data: dict containing the fields to update.
    new_file_storage: Optional FileStorage object for a new 'dataset_file'.
    """
    try:
        dataset = ChannelDataset.query.filter(ChannelDataset.dataset_uuid == dataset_uuid).first()
        if not dataset:
            return None, "Dataset not found."

        # Update metadata fields if provided in update_data
        if 'dataset_name' in update_data:
            dataset.dataset_name = update_data['dataset_name']
        if 'data_type' in update_data:
            dataset.data_type = update_data['data_type']
        if 'location_description' in update_data:
            dataset.location_description = update_data['location_description']
        if 'center_frequency_mhz' in update_data and update_data['center_frequency_mhz'] is not None:
            dataset.center_frequency_mhz = float(update_data['center_frequency_mhz'])
        if 'bandwidth_mhz' in update_data and update_data['bandwidth_mhz'] is not None:
            dataset.bandwidth_mhz = float(update_data['bandwidth_mhz'])
        if 'data_volume_groups' in update_data and update_data['data_volume_groups'] is not None:
            dataset.data_volume_groups = int(update_data['data_volume_groups'])
        if 'applicable_task_type' in update_data:
            dataset.applicable_task_type = update_data['applicable_task_type']
        
        # Handle file replacement if new_file_storage is provided
        if new_file_storage:
            original_filename = secure_filename(new_file_storage.filename)
            stored_filename = original_filename # Or a new unique name
            
            dataset_storage_dir = current_app.config.get('DATASET_FILES_DIR')
            if not dataset_storage_dir:
                return None, "File storage directory not configured."
            
            if not os.path.exists(dataset_storage_dir):
                os.makedirs(dataset_storage_dir, exist_ok=True)

            new_file_path = os.path.join(dataset_storage_dir, stored_filename)
            
            # Simple collision handling for the new file
            if os.path.exists(new_file_path):
                name_part, ext_part = os.path.splitext(stored_filename)
                stored_filename = f"{name_part}_{uuid.uuid4().hex[:8]}{ext_part}"
                new_file_path = os.path.join(dataset_storage_dir, stored_filename)

            # Delete old file if it exists and path is known
            # This assumes dataset_file_storage_path stores the filename relative to dataset_storage_dir
            if dataset.dataset_file_storage_path:
                old_file_path = os.path.join(dataset_storage_dir, dataset.dataset_file_storage_path)
                if os.path.exists(old_file_path) and old_file_path != new_file_path: # Avoid deleting the new file if names are same initially
                    try:
                        os.remove(old_file_path)
                    except Exception as e_remove:
                        # Log this error, but proceed with updating metadata and new file
                        # current_app.logger.warning(f"Could not delete old dataset file {old_file_path}: {str(e_remove)}")
                        pass 
            
            new_file_storage.save(new_file_path)
            dataset.file_name_original = original_filename
            dataset.dataset_file_storage_path = stored_filename # Update path to new file

        dataset.updated_at = datetime.utcnow()
        db.session.commit()
        
        return {"dataset_uuid": dataset.dataset_uuid}, None

    except ValueError as ve:
        db.session.rollback()
        return None, f"Invalid data format for numeric fields: {str(ve)}"
    except Exception as e:
        db.session.rollback()
        # current_app.logger.error(f"Error in update_channel_dataset_service for {dataset_uuid}: {str(e)}")
        return None, str(e) 

def delete_channel_dataset_service(dataset_uuid: str):
    """
    Service to delete a channel dataset and its associated file.
    """
    try:
        dataset = ChannelDataset.query.filter(ChannelDataset.dataset_uuid == dataset_uuid).first()
        if not dataset:
            return False, "Dataset not found."

        # Delete the associated file
        if dataset.dataset_file_storage_path:
            dataset_storage_dir = current_app.config.get('DATASET_FILES_DIR')
            if dataset_storage_dir: # Only attempt delete if directory is configured
                file_path = os.path.join(dataset_storage_dir, dataset.dataset_file_storage_path)
                if os.path.exists(file_path):
                    try:
                        os.remove(file_path)
                    except Exception as e_remove:
                        # Log this error, but proceed with deleting the DB record
                        # current_app.logger.warning(f"Could not delete dataset file {file_path}: {str(e_remove)}")
                        pass 
            # else: current_app.logger.warning("DATASET_FILES_DIR not configured, cannot delete file.")

        db.session.delete(dataset)
        db.session.commit()
        return True, None

    except Exception as e:
        db.session.rollback()
        # current_app.logger.error(f"Error in delete_channel_dataset_service for {dataset_uuid}: {str(e)}")
        return False, str(e) 