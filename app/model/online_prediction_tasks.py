from . import db
from sqlalchemy import String, Column, JSON, DateTime, Text, Integer, Float, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

class SinglePointPredictionTask(db.Model):
    __tablename__ = 'single_point_prediction_tasks'

    task_uuid = Column(String(36), primary_key=True)
    model_uuid = Column(String(36), ForeignKey('models.model_uuid'), nullable=False)
    
    prediction_mode = Column(String(20), nullable=False) # "point", "link"
    point_config = Column(JSON, nullable=False) 
    param_config = Column(JSON, nullable=False)
    
    status = Column(String(50), default="PENDING")
    
    total_points = Column(Integer, nullable=True)
    completed_points = Column(Integer, nullable=True)
    total_samples = Column(Integer, nullable=True)
    completed_samples = Column(Integer, nullable=True)
    overall_rmse_db = Column(Float, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    model = relationship("Model")
    results = relationship("SinglePointPredictionResult", back_populates="task", cascade="all, delete-orphan")

class SinglePointPredictionResult(db.Model):
    __tablename__ = 'single_point_prediction_results'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    task_uuid = Column(String(36), ForeignKey('single_point_prediction_tasks.task_uuid'), nullable=False)
    
    rx_index = Column(Integer, nullable=True)
    sample_index = Column(Integer, nullable=True)
    
    pos = Column(JSON, nullable=False)
    path_loss_db = Column(Float, nullable=False)
    distance_from_start_m = Column(Float, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    task = relationship("SinglePointPredictionTask", back_populates="results")

class SituationPredictionTask(db.Model):
    __tablename__ = 'situation_prediction_tasks'

    task_uuid = Column(String(36), primary_key=True)
    model_uuid = Column(String(36), ForeignKey('models.model_uuid'), nullable=False)

    point_config = Column(JSON, nullable=False)
    param_config = Column(JSON, nullable=False)
    status = Column(String(50), default="PENDING")

    result_heatmap_data_type = Column(String(50), nullable=True)
    result_grid_origin = Column(JSON, nullable=True)
    result_cell_size_deg = Column(JSON, nullable=True)
    result_rows = Column(Integer, nullable=True)
    result_cols = Column(Integer, nullable=True)
    result_values_storage_path = Column(String(512), nullable=True)
    result_value_unit = Column(String(20), nullable=True)
    result_url = Column(String(512), nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    model = relationship("Model")

class SmallScalePredictionTask(db.Model):
    __tablename__ = 'small_scale_prediction_tasks'

    task_uuid = Column(String(36), primary_key=True)
    model_uuid = Column(String(36), ForeignKey('models.model_uuid'), nullable=False)

    point_config = Column(JSON, nullable=False)
    param_config = Column(JSON, nullable=False)
    status = Column(String(50), default="PENDING")

    result_pdp_data_storage_path = Column(String(512), nullable=True)
    result_ber_snr_data_storage_path = Column(String(512), nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    model = relationship("Model") 