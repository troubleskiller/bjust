"""
模型详情表
"""
import uuid
import os
import shutil
import subprocess
import platform
from app import db
from flask import current_app

def generate_detail_uuid():
    """
    生成详情UUID
    :return: MODEL_DETAIL-前缀的UUID字符串
    """
    return f"MODEL_DETAIL-{uuid.uuid4().hex}"

def get_model_folder_path(model_id):
    """
    获取模型资源文件夹路径
    :param model_id: 模型ID
    :return: 模型文件夹的完整路径
    """
    return os.path.join(
        current_app.config['STORAGE_FOLDER'],
        current_app.config['MODEL_FOLDER'],
        model_id
    )

def get_architecture_image_path(model_id, filename):
    """
    获取模型架构图片存储路径
    :param model_id: 模型ID
    :param filename: 文件名
    :return: 存储路径（相对于STORAGE_FOLDER的路径）
    """
    if not filename:
        return None
    return os.path.join(
        current_app.config['MODEL_FOLDER'],
        model_id,
        current_app.config['MODEL_ARCHITECTURE_FOLDER'],
        filename
    )

def get_feature_design_image_path(model_id, filename):
    """
    获取特征设计图片存储路径
    :param model_id: 模型ID
    :param filename: 文件名
    :return: 存储路径（相对于STORAGE_FOLDER的路径）
    """
    if not filename:
        return None
    return os.path.join(
        current_app.config['MODEL_FOLDER'],
        model_id,
        current_app.config['MODEL_FEATURE_DESIGN_FOLDER'],
        filename
    )

def get_model_code_path(model_id, filename):
    """
    获取模型代码存储路径
    :param model_id: 模型ID
    :param filename: 文件名
    :return: 存储路径（相对于STORAGE_FOLDER的路径）
    """
    if not filename:
        return None
    return os.path.join(
        current_app.config['MODEL_FOLDER'],
        model_id,
        current_app.config['MODEL_CODE_FOLDER'],
        filename
    )

def get_model_env_path(model_id, filename):
    """
    获取模型环境文件存储路径
    :param model_id: 模型ID
    :param filename: 文件名
    :return: 存储路径（相对于STORAGE_FOLDER的路径）
    """
    if not filename:
        return None
    return os.path.join(
        current_app.config['MODEL_FOLDER'],
        model_id,
        current_app.config['MODEL_PYTHON_ENV_FOLDER'],
        filename
    )

class ModelDetail(db.Model):
    """模型详情表"""
    __tablename__ = 'model_detail'
    
    # 基本信息
    uuid = db.Column(db.String(50), primary_key=True, default=generate_detail_uuid)
    model_uuid = db.Column(db.String(37), db.ForeignKey('model_info.uuid', ondelete='CASCADE'), 
                        nullable=False, unique=True, comment='关联的模型UUID')
    
    # 详细信息
    description = db.Column(db.Text, nullable=False, comment='模型简介')
    architecture_image_path = db.Column(db.String(255), comment='模型架构图片路径')
    architecture_text = db.Column(db.Text, nullable=False, comment='模型架构文本')
    feature_design_image_path = db.Column(db.String(255), comment='模型特征设计图片路径')
    feature_design_text = db.Column(db.Text, nullable=False, comment='模型特征设计文本')
    
    # 代码和环境信息
    code_file_path = db.Column(db.String(255), comment='模型代码文件路径')
    env_file_path = db.Column(db.String(255), comment='模型环境文件路径')
    
    def __repr__(self):
        return f'<ModelDetail {self.uuid}>'
    
    def to_dict(self):
        """
        将模型详情转换为字典
        :return: 模型详情字典
        """
        return {
            'uuid': self.uuid,
            'model_uuid': self.model_uuid,
            'description': self.description,
            'architecture_image_path': self.architecture_image_path,
            'architecture_text': self.architecture_text,
            'feature_design_image_path': self.feature_design_image_path,
            'feature_design_text': self.feature_design_text,
            'has_code': bool(self.code_file_path),
            'has_env': bool(self.env_file_path)
        }
    
    def ensure_folders(self):
        """
        确保所有必要的文件夹存在
        """
        model_folder = get_model_folder_path(self.model_uuid)
        os.makedirs(os.path.join(model_folder, 
                                current_app.config['MODEL_ARCHITECTURE_FOLDER']), 
                   exist_ok=True)
        os.makedirs(os.path.join(model_folder, 
                                current_app.config['MODEL_FEATURE_DESIGN_FOLDER']), 
                   exist_ok=True)
        os.makedirs(os.path.join(model_folder, 
                                current_app.config['MODEL_CODE_FOLDER']), 
                   exist_ok=True)
        os.makedirs(os.path.join(model_folder, 
                                current_app.config['MODEL_PYTHON_ENV_FOLDER']), 
                   exist_ok=True)
    
    def delete_files(self):
        """
        删除所有关联的文件和文件夹
        """
        model_folder = get_model_folder_path(self.model_uuid)
        if not os.path.exists(model_folder):
            return
            
        try:
            # 首先尝试使用shutil.rmtree删除
            shutil.rmtree(model_folder, ignore_errors=True)
            
            # 检查文件夹是否还存在
            if os.path.exists(model_folder):
                # 如果还存在，使用系统命令强制删除
                if platform.system() == 'Windows':
                    # Windows系统使用rd命令
                    subprocess.run(['rd', '/s', '/q', model_folder], 
                                shell=True, 
                                check=False,
                                capture_output=True)
                else:
                    # Linux/Unix系统使用rm命令
                    subprocess.run(['rm', '-rf', model_folder], 
                                shell=False, 
                                check=False,
                                capture_output=True)
                    
            # 最后检查是否还存在
            if os.path.exists(model_folder):
                current_app.logger.warning(
                    f"无法完全删除文件夹 {model_folder}，可能需要手动清理"
                )
                
        except Exception as e:
            current_app.logger.error(
                f"删除文件夹 {model_folder} 时发生错误: {str(e)}"
            ) 