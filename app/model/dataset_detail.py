"""
数据集详情表
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
    :return: DATASET_DETAIL-前缀的UUID字符串
    """
    return f"DATASET_DETAIL-{uuid.uuid4().hex}"

def get_dataset_folder_path(dataset_id):
    """
    获取数据集资源文件夹路径
    :param dataset_id: 数据集ID
    :return: 数据集文件夹的完整路径
    """
    return os.path.join(
        current_app.config['STORAGE_FOLDER'],
        current_app.config['DATASET_FOLDER'],
        dataset_id
    )

def get_dataset_picture_path(dataset_id, picture_folder, filename):
    """
    获取数据集图片存储路径
    :param dataset_id: 数据集ID
    :param picture_folder: 图片文件夹名称
    :param filename: 文件名
    :return: 存储路径（相对于STORAGE_FOLDER的路径）
    """
    if not filename:
        return None
    return os.path.join(
        current_app.config['DATASET_FOLDER'],
        dataset_id,
        picture_folder,
        filename
    )

def get_dataset_input_path(dataset_id, filename):
    """
    获取数据集输入文件存储路径
    :param dataset_id: 数据集ID
    :param filename: 文件名
    :return: 存储路径（相对于STORAGE_FOLDER的路径）
    """
    if not filename:
        return None
    return os.path.join(
        current_app.config['DATASET_FOLDER'],
        dataset_id,
        current_app.config['DATASET_INPUT_FOLDER'],
        filename
    )

class DatasetDetail(db.Model):
    """数据集详情表"""
    __tablename__ = 'dataset_detail'
    
    # 基本信息
    uuid = db.Column(db.String(50), primary_key=True, default=generate_detail_uuid)
    dataset_uuid = db.Column(db.String(37), db.ForeignKey('dataset_info.uuid', ondelete='CASCADE'), 
                           nullable=False, unique=True, comment='关联的数据集UUID')
    
    # 详细信息
    description = db.Column(db.Text, nullable=False, comment='数据介绍')
    detail_json = db.Column(db.Text, nullable=False, comment='详细信息，JSON格式存储')
    
    # 图片信息
    picture1_path = db.Column(db.String(255), comment='图片1路径')
    picture2_path = db.Column(db.String(255), comment='图片2路径')
    
    # 输入数据路径
    input_path = db.Column(db.String(255), comment='输入文件夹路径')
    
    def __repr__(self):
        return f'<DatasetDetail {self.uuid}>'
    
    def to_dict(self):
        """
        将数据集详情转换为字典
        :return: 数据集详情字典
        """
        return {
            'uuid': self.uuid,
            'dataset_uuid': self.dataset_uuid,
            'description': self.description,
            'detail_json': self.detail_json,
            'picture1_path': self.picture1_path,
            'picture2_path': self.picture2_path,
            'input_path': self.input_path
        }
    
    def ensure_folders(self):
        """
        确保所有必要的文件夹存在
        """
        dataset_folder = get_dataset_folder_path(self.dataset_uuid)
        os.makedirs(os.path.join(dataset_folder, 
                                current_app.config['DATASET_PICTURE1_FOLDER']), 
                   exist_ok=True)
        os.makedirs(os.path.join(dataset_folder, 
                                current_app.config['DATASET_PICTURE2_FOLDER']), 
                   exist_ok=True)
        os.makedirs(os.path.join(dataset_folder, 
                                current_app.config['DATASET_INPUT_FOLDER']), 
                   exist_ok=True)
    
    def delete_files(self):
        """
        删除所有关联的文件和文件夹
        """
        dataset_folder = get_dataset_folder_path(self.dataset_uuid)
        if not os.path.exists(dataset_folder):
            return
            
        try:
            # 首先尝试使用shutil.rmtree删除
            shutil.rmtree(dataset_folder, ignore_errors=True)
            
            # 检查文件夹是否还存在
            if os.path.exists(dataset_folder):
                # 如果还存在，使用系统命令强制删除
                if platform.system() == 'Windows':
                    # Windows系统使用rd命令
                    subprocess.run(['rd', '/s', '/q', dataset_folder], 
                                shell=True, 
                                check=False,
                                capture_output=True)
                else:
                    # Linux/Unix系统使用rm命令
                    subprocess.run(['rm', '-rf', dataset_folder], 
                                shell=False, 
                                check=False,
                                capture_output=True)
                    
            # 最后检查是否还存在
            if os.path.exists(dataset_folder):
                current_app.logger.warning(
                    f"无法完全删除文件夹 {dataset_folder}，可能需要手动清理"
                )
                
        except Exception as e:
            current_app.logger.error(
                f"删除文件夹 {dataset_folder} 时发生错误: {str(e)}"
            ) 