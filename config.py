"""
应用配置文件
"""
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class Config:
    """基础配置类"""
    # Flask配置
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev')
    
    # SQLAlchemy配置
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # 文件存储目录配置
    STORAGE_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'storage')
    
    # 模型相关目录
    MODEL_FOLDER = 'model'  # 模型资源主目录
    MODEL_ARCHITECTURE_FOLDER = 'model_architecture'  # 模型架构图片目录
    MODEL_FEATURE_DESIGN_FOLDER = 'model_feature_design'  # 模型特征设计图片目录
    MODEL_CODE_FOLDER = 'model_code'  # 模型代码目录
    MODEL_PYTHON_ENV_FOLDER = 'model_python_env'  # 模型Python环境目录
    
    # 数据集相关目录
    DATASET_FOLDER = 'dataset'  # 数据集资源主目录
    DATASET_PICTURE1_FOLDER = 'picture1'  # 数据集图片1目录
    DATASET_PICTURE2_FOLDER = 'picture2'  # 数据集图片2目录
    DATASET_INPUT_FOLDER = 'input'  # 数据集输入文件目录
    
    # 验证任务相关目录
    EVALUATE_FOLDER = 'evaluate'  # 验证任务资源主目录
    EVALUATE_OUTPUT_FOLDER = 'output'  # 验证任务输出目录
    
    # 任务CSV文件存储目录
    TASK_CSV_DIR = os.path.join(STORAGE_FOLDER, 'tasks', 'csv')  # 任务CSV文件存储目录
    
    # 典型场景CSV文件存储目录
    TYPICAL_SCENARIO_CSV_DIR = os.path.join(STORAGE_FOLDER, 'typical_scenarios')  # 典型场景CSV文件存储目录
    
    # 在线推演任务相关配置
    TASK_OUTPUT_DIR = os.path.join(STORAGE_FOLDER, 'tasks')
    
    # 模型存储基础路径配置
    MODEL_STORAGE_BASE_PATH = STORAGE_FOLDER  # 模型文件存储基础路径
    
    # 日志配置
    LOG_PATH = os.getenv('LOG_PATH', 'logs')  # 日志文件路径，默认为logs目录
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')  # 日志级别
    LOG_MAX_BYTES = int(os.getenv('LOG_MAX_BYTES', str(10*1024*1024)))  # 单个日志文件最大大小（10MB）
    LOG_BACKUP_COUNT = int(os.getenv('LOG_BACKUP_COUNT', '5'))  # 保留的日志文件数量
    
    # 进程管理配置
    MAX_PROCESSES = int(os.getenv('MAX_PROCESSES', '5'))  # 最大进程数，默认为3
    
    # 其他配置
    DEBUG = os.getenv('FLASK_DEBUG', 'True').lower() in ('true', '1', 't') 