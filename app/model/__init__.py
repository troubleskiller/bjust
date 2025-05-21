"""
模型包初始化
"""
# from flask_sqlalchemy import SQLAlchemy # 如果不再需要，可以移除
import datetime # Ensure datetime is imported if used in defaults

# 添加下面这行，从父包 (app) 导入 db 实例
# 假设 app/model/ 是 app/ 的子包
from .. import db 

# Import models to register them with SQLAlchemy and for easy access
from .homepage_models import BestPracticeCase
from .model_detail import ModelDetail
from .model_info import Model, ModelInfo, ModelTypeOption, FrequencyBandOption, ApplicationScenarioOption
from .dataset_info import DatasetInfo
from .dataset_detail import DatasetDetail
from .dataset_info import ChannelDataset
from .evaluate_info import ValidationTaskTypeOption, ModelValidationTask, ModelValidationTaskModelAssociation
from .online_prediction_tasks import (
    SinglePointPredictionTask, 
    SinglePointPredictionResult, 
    SituationPredictionTask, 
    SmallScalePredictionTask
)

# 您可以定义一个基础模型，包含通用字段，例如 id, created_at, updated_at
# class BaseModel(db.Model):
#     __abstract__ = True #表示这个类自身不会在数据库中创建表
#     id = db.Column(db.Integer, primary_key=True, autoincrement=True)
#     created_at = db.Column(db.DateTime, default=datetime.utcnow)
#     updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

__all__ = ['Model', 'ModelInfo', 'ModelDetail', 'ModelTypeOption','DatasetDetail','DatasetInfo', 'FrequencyBandOption', 'ApplicationScenarioOption', 'ChannelDataset', 'ValidationTaskTypeOption', 'ModelValidationTask', 'ModelValidationTaskModelAssociation', 'SinglePointPredictionTask', 'SinglePointPredictionResult', 'SituationPredictionTask', 'SmallScalePredictionTask', 'BestPracticeCase']