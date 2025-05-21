from app.model.homepage_models import BestPracticeCase
from app import db

def get_best_practice_cases_service():
    """
    Service to fetch all best practice cases.
    """
    try:
        cases_query = BestPracticeCase.query.all()
        
        cases_data = []
        for case in cases_query:
            cases_data.append({
                "case_dir_name": case.case_dir_name,
                "case_img": case.case_img_path, # Assuming case_img_path stores the full path as needed by API
                "case_type": case.case_type,
                "case_title": case.case_title,
                "model_name": case.model_name,
                "model_type_name": case.model_type_name,
                "create_date": case.create_date_str 
            })
        return cases_data, None
    except Exception as e:
        # Log the exception e
        return None, str(e) 