from app.model.model_info import Model, ModelTypeOption, FrequencyBandOption, ApplicationScenarioOption
from app import db
from sqlalchemy import or_, and_
import math
from app.model.homepage_models import BestPracticeCase
from flask import current_app # For accessing app config for storage paths
import os

def get_models_plaza_service(page=1, page_size=10, model_name_search=None, 
                           model_type=None, frequency_bands_str=None, 
                           application_scenarios_str=None):
    """
    Service to fetch models for the Model Plaza with filtering and pagination.
    """
    try:
        query = Model.query
        filters = []

        if model_name_search:
            filters.append(Model.model_name.ilike(f"%{model_name_search}%"))
        
        if model_type:
            filters.append(Model.model_type == model_type)

        if frequency_bands_str:
            bands = [band.strip() for band in frequency_bands_str.split(',') if band.strip()]
            if bands:
                band_filters = []
                for band in bands:
                    # Assuming Model.frequency_bands is a JSON array of strings
                    # The exact syntax for JSON array containment might vary by DB (e.g., using func.json_contains)
                    # For PostgreSQL, you might use Model.frequency_bands.contains([band])
                    # Using a generic approach here, which might need DB-specific functions for optimization
                    band_filters.append(Model.frequency_bands.astext.ilike(f'%"{band}"%')) # Basic string search in JSON text form
                if band_filters:
                    filters.append(or_(*band_filters))

        if application_scenarios_str:
            scenarios = [scenario.strip() for scenario in application_scenarios_str.split(',') if scenario.strip()]
            if scenarios:
                scenario_filters = []
                for scenario in scenarios:
                    # Similar to frequency_bands, using a generic JSON text search
                    scenario_filters.append(Model.application_scenarios.astext.ilike(f'%"{scenario}"%'))
                if scenario_filters:
                    filters.append(or_(*scenario_filters))

        if filters:
            query = query.filter(and_(*filters))
        
        query = query.order_by(Model.updated_at.desc())
        
        paginated_models = query.paginate(page=page, per_page=page_size, error_out=False)
        
        models_data = []
        for model in paginated_models.items:
            models_data.append({
                "model_uuid": model.model_uuid,
                "model_name": model.model_name,
                "model_type": model.model_type,
                "frequency_bands": model.frequency_bands if isinstance(model.frequency_bands, list) else [],
                "application_scenarios": model.application_scenarios if isinstance(model.application_scenarios, list) else [],
                "update_time": model.updated_at.isoformat() + "Z", # As per example format
                "can_be_used_for_validation": model.can_be_used_for_validation
            })
            
        pagination_info = {
            "current_page": paginated_models.page,
            "page_size": paginated_models.per_page,
            "total_items": paginated_models.total,
            "total_pages": paginated_models.pages
        }
        
        return models_data, pagination_info, None

    except Exception as e:
        # current_app.logger.error(f"Error in get_models_plaza_service: {str(e)}")
        return None, None, str(e) 

def get_grouped_models_service():
    """
    Service to fetch models grouped by their type for the model detail introduction page.
    """
    try:
        model_type_options = ModelTypeOption.query.order_by(ModelTypeOption.id).all()
        
        grouped_models_data = []
        
        for type_option in model_type_options:
            models_in_group = Model.query.filter(Model.model_type == type_option.value) \
                                       .order_by(Model.model_name).all()
            
            # Decide whether to include groups with no models based on requirements
            # if not models_in_group:
            #     continue 

            group_data = {
                "group_name": type_option.label,
                "group_id": type_option.value,
                "models": [
                    {
                        "model_uuid": model.model_uuid,
                        "model_name": model.model_name
                    }
                    for model in models_in_group
                ]
            }
            grouped_models_data.append(group_data)
            
        return grouped_models_data, None
    except Exception as e:
        # current_app.logger.error(f"Error in get_grouped_models_service: {str(e)}")
        return None, str(e) 

def get_model_full_details_service(model_uuid: str):
    """
    Service to fetch full details for a specific model.
    """
    try:
        model = Model.query.filter(Model.model_uuid == model_uuid).first()
        if not model:
            return None, "Model not found."

        # 1. Fetch Markdown document content
        markdown_content = ""
        if model.model_doc_storage_path:
            # Construct the full path to the markdown file
            # This assumes model_doc_storage_path is relative to a known base storage directory
            # Example: model_doc_storage_path = "models_docs/uuid-model-001/doc.md"
            # Needs to be combined with app.config['STORAGE_FOLDER'] or similar
            # For now, let's assume it's an absolute path or resolvable from a base
            doc_full_path = os.path.join(current_app.config.get('MODEL_STORAGE_BASE_PATH', '/app/storage'), model.model_doc_storage_path)
            try:
                # Ensure the path is safe to prevent directory traversal if path comes from user input in other contexts
                # Here it's from DB, so it should be safer, but good to be mindful.
                if os.path.exists(doc_full_path) and os.path.isfile(doc_full_path):
                    with open(doc_full_path, 'r', encoding='utf-8') as f:
                        markdown_content = f.read()
                else:
                    markdown_content = "Markdown document not found at the specified path."
            except Exception as doc_exc:
                markdown_content = f"Error reading markdown document: {str(doc_exc)}"
        else:
            markdown_content = "No markdown document path specified for this model."

        # 2. Fetch related practice cases preview
        practice_cases_preview = []
        if model.model_name: # Ensure model_name exists to search by
            # This is a simple string search. If model names in BestPracticeCase.model_name are comma-separated,
            # we need a more robust way to check if the current model's name is part of that list.
            # For now, using a simple substring search on the comma-separated string.
            # A better approach would be to normalize this (e.g., store model associations in a separate table or use JSON arrays).
            # cases_related = BestPracticeCase.query.filter(BestPracticeCase.model_name.ilike(f"%{model.model_name}%")).limit(5).all()
            
            # More robust check for comma-separated list:
            all_cases = BestPracticeCase.query.all()
            related_cases_found = []
            for case in all_cases:
                if case.model_name:
                    model_names_in_case = [name.strip() for name in case.model_name.split(',')]
                    if model.model_name in model_names_in_case:
                        related_cases_found.append(case)
                        if len(related_cases_found) >= 5: # Limit to 5 previews
                            break
            
            for case in related_cases_found:
                practice_cases_preview.append({
                    "case_dir_name": case.case_dir_name,
                    "case_img": case.case_img_path, # Assuming this is the correct path for API response
                    "case_title": case.case_title,
                    "case_type": case.case_type
                })

        # 3. Overview summary (using model_description as a fallback or primary source)
        overview_summary = model.model_description # Or a dedicated field like model.overview_summary if it exists

        model_details_data = {
            "model_uuid": model.model_uuid,
            "model_name": model.model_name,
            "model_type": model.model_type,
            "model_description": model.model_description,
            "frequency_bands": model.frequency_bands if isinstance(model.frequency_bands, list) else [],
            "application_scenarios": model.application_scenarios if isinstance(model.application_scenarios, list) else [],
            "update_time": model.updated_at.isoformat() + "Z",
            "markdown_doc_content": markdown_content,
            "practice_cases_preview": practice_cases_preview,
            "overview_summary": overview_summary
        }
        
        return model_details_data, None

    except Exception as e:
        # current_app.logger.error(f"Error in get_model_full_details_service for {model_uuid}: {str(e)}")
        return None, str(e) 

def get_model_filter_options_service():
    """
    Service to fetch filter options for the Model Plaza.
    """
    try:
        model_types = ModelTypeOption.query.order_by(ModelTypeOption.label).all()
        frequency_bands = FrequencyBandOption.query.order_by(FrequencyBandOption.label).all()
        application_scenarios = ApplicationScenarioOption.query.order_by(ApplicationScenarioOption.label).all()

        options_data = {
            "model_types": [
                {"value": mt.value, "label": mt.label} for mt in model_types
            ],
            "frequency_bands": [
                {"value": fb.value, "label": fb.label} for fb in frequency_bands
            ],
            "application_scenarios": [
                {"value": asc.value, "label": asc.label} for asc in application_scenarios
            ]
        }
        return options_data, None
    except Exception as e:
        # current_app.logger.error(f"Error in get_model_filter_options_service: {str(e)}")
        return None, str(e) 