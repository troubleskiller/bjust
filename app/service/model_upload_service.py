"""
模型上传服务
"""
import os
import shutil
import zipfile
import pandas as pd
from datetime import datetime
from app import db
from app.model import ModelInfo, ModelDetail
from flask import current_app
from app.utils.safe_extractor import SafeExtractor

class ModelUploadService:
    """模型上传服务类"""
    
    @staticmethod
    def process_model_upload(zip_file_path, temp_extract_path):
        """
        处理模型上传
        :param zip_file_path: 上传的压缩包路径
        :param temp_extract_path: 临时解压目录
        :return: 创建的模型UUID
        """
        try:
            # 解压文件
            with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
                zip_ref.extractall(temp_extract_path)
            # 读取模型信息
            excel_path = os.path.join(temp_extract_path, 'model_information.xlsx')
            model_info = ModelUploadService._read_model_information(excel_path)
            
            # 创建模型记录
            model = ModelInfo(
                name=model_info['模型名称'],
                task_type=int(model_info['模型任务']),
                output_type=model_info['模型输出'],
                model_category=model_info['模型类别'],
                application_scenario=model_info['应用场景'],
                test_data_count=0,  # 初始测试数据数量为0
                training_date=model_info['模型训练时间'],  # 现在这是一个datetime对象
                parameter_count=model_info['模型参数量'],
                convergence_time=model_info['模型收敛时长']
            )
            
            # 创建模型详情记录
            model_detail = ModelDetail(
                description=model_info['模型简介'],
                architecture_text='',  # 暂时为空，后续可以添加
                feature_design_text=model_info['模型特征设计']
            )
            
            # 关联模型和详情
            model.detail = model_detail
            
            # 保存到数据库以获取UUID
            db.session.add(model)
            db.session.commit()
            
            # 确保目标目录存在
            model_detail.ensure_folders()
            
            # 复制文件到最终位置
            ModelUploadService._copy_model_files(temp_extract_path, model.uuid)
            
            # 解压Python环境
            ModelUploadService._extract_python_env(temp_extract_path, model.uuid)
            
            # 更新文件路径
            ModelUploadService._update_file_paths(model_detail, model.uuid)
            db.session.commit()
            
            return model.uuid
            
        except Exception as e:
            db.session.rollback()
            # 清理已创建的文件夹
            if 'model' in locals():
                model_folder = os.path.join(
                    current_app.config['STORAGE_FOLDER'],
                    current_app.config['MODEL_FOLDER'],
                    model.uuid
                )
                if os.path.exists(model_folder):
                    shutil.rmtree(model_folder, ignore_errors=True)
            raise e
        finally:
            # 清理临时文件
            if os.path.exists(temp_extract_path):
                shutil.rmtree(temp_extract_path, ignore_errors=True)
    
    @staticmethod
    def _read_model_information(excel_path):
        """
        读取模型信息Excel文件
        :param excel_path: Excel文件路径
        :return: 模型信息字典
        """
        # 读取Excel文件，将日期列解析为datetime
        df = pd.read_excel(excel_path, parse_dates=['值'])
        
        # 创建结果字典
        result = {}
        for _, row in df.iterrows():
            field_name = row['字段名']
            value = row['值']
            
            # 特殊处理日期字段
            if field_name == '模型训练时间':
                if pd.isna(value):
                    value = datetime.now()  # 如果日期为空，使用当前时间
                elif isinstance(value, (int, float)):
                    # 如果是Excel序列号，转换为datetime
                    value = pd.Timestamp.fromordinal(int(value) + 693594).to_pydatetime()
                elif isinstance(value, str):
                    # 如果是字符串，尝试解析
                    try:
                        value = datetime.strptime(value, '%Y年%m月%d日')
                    except ValueError:
                        value = datetime.now()
            
            result[field_name] = value
            
        return result
    
    @staticmethod
    def _copy_model_files(source_path, model_uuid):
        """
        复制模型文件到存储目录
        :param source_path: 源文件目录
        :param model_uuid: 模型UUID
        """
        storage_base = os.path.join(
            current_app.config['STORAGE_FOLDER'],
            current_app.config['MODEL_FOLDER'],
            model_uuid
        )
        
        # 复制架构图片
        arch_src = os.path.join(source_path, 'model_architecture')
        arch_dst = os.path.join(storage_base, current_app.config['MODEL_ARCHITECTURE_FOLDER'])
        if os.path.exists(arch_src):
            for file in os.listdir(arch_src):
                shutil.copy2(
                    os.path.join(arch_src, file),
                    os.path.join(arch_dst, file)
                )
        
        # 复制特征设计图片
        feature_src = os.path.join(source_path, 'model_feature_design')
        feature_dst = os.path.join(storage_base, current_app.config['MODEL_FEATURE_DESIGN_FOLDER'])
        if os.path.exists(feature_src):
            for file in os.listdir(feature_src):
                shutil.copy2(
                    os.path.join(feature_src, file),
                    os.path.join(feature_dst, file)
                )
        
        # 复制代码文件
        code_src = os.path.join(source_path, 'model_code')
        code_dst = os.path.join(storage_base, current_app.config['MODEL_CODE_FOLDER'])
        if os.path.exists(code_src):
            for item in os.listdir(code_src):
                s = os.path.join(code_src, item)
                d = os.path.join(code_dst, item)
                if os.path.isdir(s):
                    shutil.copytree(s, d)
                else:
                    shutil.copy2(s, d)
    
    @staticmethod
    def _extract_python_env(source_path, model_uuid):
        """
        解压Python环境文件
        :param source_path: 源文件目录
        :param model_uuid: 模型UUID
        """
        env_zip = os.path.join(source_path, 'model_python_env', 'python_env.zip')
        if os.path.exists(env_zip):
            env_dst = os.path.join(
                current_app.config['STORAGE_FOLDER'],
                current_app.config['MODEL_FOLDER'],
                model_uuid,
                current_app.config['MODEL_PYTHON_ENV_FOLDER']
            )
            # 使用安全解压器解压Python环境
            extractor = SafeExtractor(env_zip, env_dst)
            if not extractor.extract_all():
                raise Exception("Python环境解压失败")
    
    @staticmethod
    def _update_file_paths(model_detail, model_uuid):
        """
        更新模型详情中的文件路径
        :param model_detail: 模型详情对象
        :param model_uuid: 模型UUID
        """
        # 查找并更新架构图片路径
        arch_folder = os.path.join(
            current_app.config['STORAGE_FOLDER'],
            current_app.config['MODEL_FOLDER'],
            model_uuid,
            current_app.config['MODEL_ARCHITECTURE_FOLDER']
        )
        if os.path.exists(arch_folder):
            files = os.listdir(arch_folder)
            if files:
                model_detail.architecture_image_path = os.path.join(
                    current_app.config['MODEL_FOLDER'],
                    model_uuid,
                    current_app.config['MODEL_ARCHITECTURE_FOLDER'],
                    files[0]
                )
        
        # 查找并更新特征设计图片路径
        feature_folder = os.path.join(
            current_app.config['STORAGE_FOLDER'],
            current_app.config['MODEL_FOLDER'],
            model_uuid,
            current_app.config['MODEL_FEATURE_DESIGN_FOLDER']
        )
        if os.path.exists(feature_folder):
            files = os.listdir(feature_folder)
            if files:
                model_detail.feature_design_image_path = os.path.join(
                    current_app.config['MODEL_FOLDER'],
                    model_uuid,
                    current_app.config['MODEL_FEATURE_DESIGN_FOLDER'],
                    files[0]
                )
        
        # 更新代码文件路径（使用main.py作为标识）
        code_path = os.path.join(
            current_app.config['MODEL_FOLDER'],
            model_uuid,
            current_app.config['MODEL_CODE_FOLDER'],
            'main.py'
        )
        model_detail.code_file_path = code_path
        
        # 更新环境文件路径
        env_path = os.path.join(
            current_app.config['MODEL_FOLDER'],
            model_uuid,
            current_app.config['MODEL_PYTHON_ENV_FOLDER']
        )
        if os.path.exists(os.path.join(current_app.config['STORAGE_FOLDER'], env_path)):
            model_detail.env_file_path = env_path