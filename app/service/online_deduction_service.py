from app.model.model_info import Model
from app import db

# This mapping might need to be more sophisticated or stored elsewhere (e.g., in the database)
# if a model can belong to multiple task types or if task_types are more dynamic.
TASK_TYPE_TO_MODEL_TYPE_MAPPING = {
    "single_point_prediction": "large_scale",
    "situation_prediction": "situation_awareness",
    "small_scale_prediction": "small_scale",
}

def get_online_models_by_task_type_service(task_type: str):
    """
    Service to fetch models available for a specific online deduction task type.
    """
    try:
        target_model_type = TASK_TYPE_TO_MODEL_TYPE_MAPPING.get(task_type)
        if not target_model_type:
            return [], "Invalid task_type specified."

        models_query = Model.query.filter(Model.model_type == target_model_type).all()
        
        models_data = []
        for model in models_query:
            # Assuming tiff_image_storage_path can serve as model_img
            # And model_doc_storage_path can serve as a base for model_doc_url
            # These might need adjustment based on how static files/docs are served.
            model_img = model.tiff_image_storage_path or "/path/to/default_model_thumb.jpg" # Placeholder for default
            model_doc_url = f"/models/{model.model_uuid}/documentation" # Constructing as per API doc example
            # If model_doc_storage_path is already a URL or a specific relative path, use that.
            # model_doc_url = model.model_doc_storage_path 

            models_data.append({
                "model_uuid": model.model_uuid,
                "model_name": model.model_name,
                "model_description": model.model_description,
                "model_img": model_img, 
                "model_doc_url": model_doc_url 
            })
        return models_data, None
    except Exception as e:
        # Log the exception e (e.g., current_app.logger.error(...))
        return None, str(e) 