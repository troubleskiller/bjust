"""
模型验证任务表
"""
from datetime import datetime
import uuid
import os
import shutil
import subprocess
import platform
from enum import Enum
from app import db
from flask import current_app
from sqlalchemy import String, Column, JSON, DateTime, Text, Integer, Float, ForeignKey
from sqlalchemy.orm import relationship

class EvaluateStatusType(Enum):
    """验证任务状态枚举"""
    NOT_STARTED = 'NOT_STARTED'
    IN_PROGRESS = 'IN_PROGRESS'
    COMPLETED = 'COMPLETED'
    ABORTED = 'ABORTED'

def generate_evaluate_uuid():
    """
    生成验证任务UUID
    :return: EVALUATE-前缀的UUID字符串
    """
    return f"EVALUATE-{uuid.uuid4().hex}"

def get_evaluate_folder_path(evaluate_id):
    """
    获取验证任务资源文件夹路径
    :param evaluate_id: 验证任务ID
    :return: 验证任务文件夹的完整路径
    """
    return os.path.join(
        current_app.config['STORAGE_FOLDER'],
        current_app.config['EVALUATE_FOLDER'],
        evaluate_id
    )

def get_evaluate_output_path(evaluate_id, filename):
    """
    获取验证任务输出文件存储路径
    :param evaluate_id: 验证任务ID
    :param filename: 文件名
    :return: 存储路径（相对于STORAGE_FOLDER的路径）
    """
    if not filename:
        return None
    return os.path.join(
        current_app.config['EVALUATE_FOLDER'],
        evaluate_id,
        current_app.config['EVALUATE_OUTPUT_FOLDER'],
        filename
    )

class EvaluateInfo(db.Model):
    """模型验证任务表"""
    __tablename__ = 'evaluate_info'
    
    # 基本信息
    uuid = db.Column(db.String(37), primary_key=True, default=generate_evaluate_uuid)
    evaluate_type = db.Column(db.Integer, nullable=False, comment='验证任务类型(1-4)')
    
    # 关联信息
    model_uuid = db.Column(db.String(37), db.ForeignKey('model_info.uuid', ondelete='SET NULL'), 
                         nullable=True, comment='关联的模型UUID')
    dataset_uuid = db.Column(db.String(37), db.ForeignKey('dataset_info.uuid', ondelete='SET NULL'), 
                           nullable=True, comment='关联的数据集UUID')
    
    # 任务状态
    evaluate_status = db.Column(db.String(20), nullable=False, 
                              default=EvaluateStatusType.NOT_STARTED.value, comment='验证任务状态')
    start_time = db.Column(db.DateTime, nullable=False, comment='任务开始时间')
    end_time = db.Column(db.DateTime, nullable=True, comment='任务结束时间')
    
    # 其他信息
    extra_parameter = db.Column(db.Text, nullable=True, comment='额外参数')
    
    def __repr__(self):
        return f'<EvaluateInfo {self.uuid}>'
    
    def to_dict(self):
        """
        将验证任务信息转换为字典
        :return: 验证任务信息字典
        """
        return {
            'uuid': self.uuid,
            'evaluate_type': self.evaluate_type,
            'model_uuid': self.model_uuid,
            'dataset_uuid': self.dataset_uuid,
            'evaluate_status': self.evaluate_status,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'extra_parameter': self.extra_parameter
        }
    
    def ensure_folders(self):
        """
        确保所有必要的文件夹存在
        """
        evaluate_folder = get_evaluate_folder_path(self.uuid)
        os.makedirs(os.path.join(evaluate_folder, 
                                current_app.config['EVALUATE_OUTPUT_FOLDER']), 
                   exist_ok=True)
    
    def delete_files(self):
        """
        删除所有关联的文件和文件夹
        """
        evaluate_folder = get_evaluate_folder_path(self.uuid)
        if not os.path.exists(evaluate_folder):
            return
            
        try:
            # 首先尝试使用shutil.rmtree删除
            shutil.rmtree(evaluate_folder, ignore_errors=True)
            
            # 检查文件夹是否还存在
            if os.path.exists(evaluate_folder):
                # 如果还存在，使用系统命令强制删除
                if platform.system() == 'Windows':
                    # Windows系统使用rd命令
                    subprocess.run(['rd', '/s', '/q', evaluate_folder], 
                                shell=True, 
                                check=False,
                                capture_output=True)
                else:
                    # Linux/Unix系统使用rm命令
                    subprocess.run(['rm', '-rf', evaluate_folder], 
                                shell=False, 
                                check=False,
                                capture_output=True)
                    
            # 最后检查是否还存在
            if os.path.exists(evaluate_folder):
                current_app.logger.warning(
                    f"无法完全删除文件夹 {evaluate_folder}，可能需要手动清理"
                )
                
        except Exception as e:
            current_app.logger.error(
                f"删除文件夹 {evaluate_folder} 时发生错误: {str(e)}"
            ) 

class ValidationTaskTypeOption(db.Model):
    __tablename__ = 'validation_task_type_options'
    id = Column(Integer, primary_key=True, autoincrement=True)
    task_type_id_str = Column(String(50), unique=True, nullable=False) # 例如: "single_point_link"
    name = Column(String(100), nullable=False) # 例如: "单点预测-链路模式验证"

class ModelValidationTask(db.Model):
    __tablename__ = 'model_validation_tasks'

    validation_task_uuid = Column(String(36), primary_key=True)
    validation_task_name = Column(String(255), nullable=True)
    
    task_type_id_str = Column(String(50), ForeignKey('validation_task_type_options.task_type_id_str'), nullable=False)
    dataset_uuid = Column(String(36), ForeignKey('channel_datasets.dataset_uuid'), nullable=False)
    
    param_config = Column(JSON, nullable=True) # 小尺度预测任务需要的额外参数
    
    status = Column(String(50), default="PENDING") # "PENDING", "IN_PROGRESS", "COMPLETED", "FAILED", "PARTIAL_COMPLETE"
    error_message = Column(Text, nullable=True)
    
    actual_data_storage_path = Column(String(512), nullable=True) # 存储用于对比的实测数据路径

    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    dataset = relationship("ChannelDataset")
    task_type_option = relationship("ValidationTaskTypeOption")
    models_associated = relationship("ModelValidationTaskModelAssociation", back_populates="validation_task", cascade="all, delete-orphan")

class ModelValidationTaskModelAssociation(db.Model):
    __tablename__ = 'model_validation_task_model_associations'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    validation_task_uuid = Column(String(36), ForeignKey('model_validation_tasks.validation_task_uuid'), nullable=False)
    model_uuid = Column(String(36), ForeignKey('models.model_uuid'), nullable=False)
    
    status_for_model = Column(String(50), default="PENDING") # 此模型在验证任务中的状态
    error_message_for_model = Column(Text, nullable=True)
    model_specific_result_storage_path = Column(String(512), nullable=True) # 此模型特定结果的存储路径

    validation_task = relationship("ModelValidationTask", back_populates="models_associated")
    model = relationship("Model") 