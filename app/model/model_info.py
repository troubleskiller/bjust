"""
模型基础信息表
"""
from datetime import datetime
import uuid
from . import db
from sqlalchemy import String, Column, JSON, DateTime, Boolean, Text, Integer, ForeignKey
from sqlalchemy.orm import relationship

def generate_model_uuid():
    """
    生成模型UUID
    :return: MODEL-前缀的UUID字符串
    """
    return f"MODEL-{uuid.uuid4().hex}"

class Model(db.Model):
    __tablename__ = 'models'

    model_uuid = Column(String(36), primary_key=True)
    model_name = Column(String(255), nullable=False)
    model_type = Column(String(50), nullable=False) # 例如: "large_scale", "situation_awareness", "small_scale"
    
    frequency_bands = Column(JSON) # 字符串数组
    application_scenarios = Column(JSON) # 字符串数组
    
    model_description = Column(Text, nullable=True)
    
    model_doc_storage_path = Column(String(512), nullable=True) # 模型文档存储路径
    tiff_image_storage_path = Column(String(512), nullable=True) # TIFF图像存储路径
    model_zip_storage_path = Column(String(512), nullable=True) # 模型ZIP包存储路径
    dataset_for_validation_zip_storage_path = Column(String(512), nullable=True) # 验证数据集ZIP包存储路径

    can_be_used_for_validation = Column(Boolean, default=False)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # relationships (如果需要，可以在另一端用 back_populates="model" 配合)
    # online_single_point_tasks = relationship("SinglePointPredictionTask", backref="model")
    # online_situation_tasks = relationship("SituationPredictionTask", backref="model")
    # online_small_scale_tasks = relationship("SmallScalePredictionTask", backref="model")
    # validation_associations = relationship("ModelValidationTaskModelAssociation", backref="model")

class ModelTypeOption(db.Model):
    __tablename__ = 'model_type_options'
    id = Column(Integer, primary_key=True, autoincrement=True)
    value = Column(String(50), unique=True, nullable=False) # 例如: "large_scale"
    label = Column(String(100), nullable=False) # 例如: "大尺度模型"

class FrequencyBandOption(db.Model):
    __tablename__ = 'frequency_band_options'
    id = Column(Integer, primary_key=True, autoincrement=True)
    value = Column(String(50), unique=True, nullable=False) # 例如: "sub_6GHz"
    label = Column(String(100), nullable=False) # 例如: "Sub-6GHz"

class ApplicationScenarioOption(db.Model):
    __tablename__ = 'application_scenario_options'
    id = Column(Integer, primary_key=True, autoincrement=True)
    value = Column(String(50), unique=True, nullable=False) # 例如: "urban_macro"
    label = Column(String(100), nullable=False) # 例如: "城市宏"

class ModelInfo(db.Model):
    """模型基础信息表"""
    __tablename__ = 'model_info'
    
    # 基本信息
    uuid = db.Column(db.String(37), primary_key=True, default=generate_model_uuid)
    name = db.Column(db.String(100), nullable=False, comment='模型名称')
    task_type = db.Column(db.Integer, nullable=False, comment='模型任务(1-4)')
    output_type = db.Column(db.String(100), nullable=False, comment='模型输出')
    
    # 分类信息
    model_category = db.Column(db.String(50), nullable=False, comment='模型类别')
    application_scenario = db.Column(db.String(50), nullable=False, comment='应用场景')
    test_data_count = db.Column(db.Integer, nullable=False, comment='测试数据数量')
    training_date = db.Column(db.DateTime, nullable=False, comment='模型训练日期')
    
    # 技术指标
    parameter_count = db.Column(db.String(50), nullable=False, comment='模型参数量')
    convergence_time = db.Column(db.String(50), nullable=False, comment='模型收敛时长')
    
    # 更新时间
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, 
                          onupdate=datetime.utcnow, comment='更新时间')
    
    # 关联详情表
    detail = db.relationship('ModelDetail', backref='model', uselist=False, 
                           cascade='all, delete-orphan', single_parent=True)
    
    def __repr__(self):
        return f'<ModelInfo {self.name}>'
    
    def to_dict(self):
        """
        将模型转换为字典
        :return: 模型信息字典
        """
        return {
            'uuid': self.uuid,
            'name': self.name,
            'task_type': self.task_type,
            'output_type': self.output_type,
            'model_category': self.model_category,
            'application_scenario': self.application_scenario,
            'test_data_count': self.test_data_count,
            'training_date': self.training_date.isoformat(),
            'parameter_count': self.parameter_count,
            'convergence_time': self.convergence_time,
            'updated_at': self.updated_at.isoformat()
        } 