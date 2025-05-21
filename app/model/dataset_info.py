"""
数据集基础信息表
"""
from datetime import datetime
import uuid
from .. import db
from sqlalchemy import String, Column, DateTime, Text, Integer, Float, Boolean

def generate_dataset_uuid():
    """
    生成数据集UUID
    :return: DATASET-前缀的UUID字符串
    """
    return f"DATASET-{uuid.uuid4().hex}"

class DatasetInfo(db.Model):
    """数据集基础信息表"""
    __tablename__ = 'dataset_info'
    
    # 基本信息
    uuid = db.Column(db.String(37), primary_key=True, default=generate_dataset_uuid)
    dataset_type = db.Column(db.Integer, nullable=False, comment='数据集类型(1-3)')
    category = db.Column(db.String(50), nullable=False, comment='类别')
    scenario = db.Column(db.String(50), nullable=False, comment='场景')
    location = db.Column(db.String(100), nullable=False, comment='地点')
    
    # 技术参数
    center_frequency = db.Column(db.String(50), nullable=False, comment='中心频率')
    bandwidth = db.Column(db.String(50), nullable=False, comment='带宽')
    data_group_count = db.Column(db.String(50), nullable=False, comment='数据组数')
    applicable_models = db.Column(db.Text, nullable=False, comment='适用模型，多个模型用英文逗号分隔')
    
    # 更新时间
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, 
                          onupdate=datetime.utcnow, comment='更新时间')
    
    # 关联详情表
    detail = db.relationship('DatasetDetail', backref='dataset', uselist=False, 
                           cascade='all, delete-orphan', single_parent=True)
    
    def __repr__(self):
        return f'<DatasetInfo {self.category}>'
    
    def to_dict(self):
        """
        将数据集信息转换为字典
        :return: 数据集信息字典
        """
        return {
            'uuid': self.uuid,
            'dataset_type': self.dataset_type,
            'category': self.category,
            'scenario': self.scenario,
            'location': self.location,
            'center_frequency': self.center_frequency,
            'bandwidth': self.bandwidth,
            'data_group_count': self.data_group_count,
            'applicable_models': self.applicable_models,
            'updated_at': self.updated_at.isoformat()
        }

class ChannelDataset(db.Model):
    __tablename__ = 'channel_datasets'

    dataset_uuid = Column(String(36), primary_key=True)
    dataset_name = Column(String(255), nullable=False)
    data_type = Column(String(50), nullable=False) # "real_measurement", "simulation"
    location_description = Column(Text, nullable=True)
    center_frequency_mhz = Column(Float, nullable=True)
    bandwidth_mhz = Column(Float, nullable=True)
    data_volume_groups = Column(Integer, nullable=True)
    applicable_task_type = Column(String(100), nullable=True) # 例如: "single_point_prediction"

    file_name_original = Column(String(255), nullable=True) # 原始上传文件名
    dataset_file_storage_path = Column(String(512), nullable=False) # 数据集文件存储路径

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # relationships
    # validation_tasks = relationship("ModelValidationTask", backref="dataset") 