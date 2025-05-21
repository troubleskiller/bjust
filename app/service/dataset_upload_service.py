"""
数据集上传服务
"""
import os
import shutil
import pandas as pd
import json
from datetime import datetime
from app import db
from app.model import DatasetInfo, DatasetDetail
from flask import current_app
from app.utils.safe_extractor import SafeExtractor

class DatasetUploadService:
    """数据集上传服务类"""
    
    @staticmethod
    def process_dataset_upload(zip_file_path, temp_extract_path):
        """
        处理数据集上传
        :param zip_file_path: 上传的压缩包路径
        :param temp_extract_path: 临时解压目录
        :return: 创建的数据集UUID
        """
        try:
            # 解压文件
            # with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
            #     zip_ref.extractall(temp_extract_path)
            extractor = SafeExtractor(zip_file_path, temp_extract_path)
            if not extractor.extract_all():
                raise Exception("数据集解压失败")
            
            # 读取数据集信息
            excel_path = os.path.join(temp_extract_path, 'dataset_information.xlsx')
            dataset_info = DatasetUploadService._read_dataset_information(excel_path)
            
            # 创建数据集记录
            dataset = DatasetInfo(
                dataset_type=int(dataset_info['数据集类型']),
                category=dataset_info['类别'],
                scenario=dataset_info['场景'],
                location=dataset_info['地点'],
                center_frequency=dataset_info['中心频率'],
                bandwidth=dataset_info['带宽'],
                data_group_count=dataset_info['数据组数'],
                applicable_models=dataset_info['适用模型']
            )
            
            # 创建数据集详情记录
            dataset_detail = DatasetDetail(
                description=dataset_info['数据介绍'],
                detail_json=json.dumps(dataset_info['details'], ensure_ascii=False)
            )
            
            # 关联数据集和详情
            dataset.detail = dataset_detail
            
            # 保存到数据库以获取UUID
            db.session.add(dataset)
            db.session.commit()
            
            # 确保目标目录存在
            dataset_detail.ensure_folders()
            
            # 复制文件到最终位置
            DatasetUploadService._copy_dataset_files(temp_extract_path, dataset.uuid)
            
            # 更新文件路径
            DatasetUploadService._update_file_paths(dataset_detail, dataset.uuid)
            db.session.commit()
            
            return dataset.uuid
            
        except Exception as e:
            db.session.rollback()
            # 清理已创建的文件夹
            if 'dataset' in locals():
                dataset_folder = os.path.join(
                    current_app.config['STORAGE_FOLDER'],
                    current_app.config['DATASET_FOLDER'],
                    dataset.uuid
                )
                if os.path.exists(dataset_folder):
                    shutil.rmtree(dataset_folder, ignore_errors=True)
            raise e
        finally:
            # 清理临时文件
            if os.path.exists(temp_extract_path):
                shutil.rmtree(temp_extract_path, ignore_errors=True)
    
    @staticmethod
    def _read_dataset_information(excel_path):
        """
        读取数据集信息Excel文件
        :param excel_path: Excel文件路径
        :return: 数据集信息字典
        """
        # 读取Excel文件
        df = pd.read_excel(excel_path)
        
        # 创建结果字典
        result = {}
        details = {}
        
        # 定义需要日期转换的字段
        date_fields = ['测量日期']  # 根据实际需要添加其他日期字段
        
        for _, row in df.iterrows():
            field_name = str(row['字段名']).strip() if pd.notna(row['字段名']) else ''
            value = row['值']
            
            # 跳过空行
            if not field_name:
                continue
                
            # 处理日期类型
            if field_name in date_fields:
                if pd.isna(value):
                    value = datetime.now()  # 如果日期为空，使用当前时间
                elif isinstance(value, (int, float)):
                    # 如果是Excel序列号，转换为datetime
                    value = pd.Timestamp.fromordinal(int(value) + 693594).strftime('%Y年%m月%d日')
                elif isinstance(value, str):
                    # 如果是字符串，尝试解析
                    try:
                        value = datetime.strptime(value, '%Y年%m月%d日').strftime('%Y年%m月%d日')
                    except:
                        value = str(value)
            elif pd.isna(value):
                value = ''
            else:
                # 对于非日期字段，保持原始数值类型
                if isinstance(value, (int, float)):
                    value = float(value)  # 保持数值类型
                else:
                    value = str(value)
            
            # 将基本信息存入result
            if field_name in ['数据集类型', '类别', '场景', '地点', '中心频率', 
                            '带宽', '数据组数', '适用模型', '数据介绍']:
                result[field_name] = value
            # 将其他信息存入details
            else:
                details[field_name] = value
        
        result['details'] = details
        return result
    
    @staticmethod
    def _copy_dataset_files(source_path, dataset_uuid):
        """
        复制数据集文件到存储目录
        :param source_path: 源文件目录
        :param dataset_uuid: 数据集UUID
        """
        storage_base = os.path.join(
            current_app.config['STORAGE_FOLDER'],
            current_app.config['DATASET_FOLDER'],
            dataset_uuid
        )
        
        # 复制输入文件夹
        input_src = os.path.join(source_path, 'input')
        input_dst = os.path.join(storage_base, current_app.config['DATASET_INPUT_FOLDER'])
        if os.path.exists(input_src):
            for item in os.listdir(input_src):
                s = os.path.join(input_src, item)
                d = os.path.join(input_dst, item)
                if os.path.isdir(s):
                    shutil.copytree(s, d)
                else:
                    shutil.copy2(s, d)
        
        # 复制图片1
        picture1_src = os.path.join(source_path, 'picture1')
        picture1_dst = os.path.join(storage_base, current_app.config['DATASET_PICTURE1_FOLDER'])
        if os.path.exists(picture1_src):
            for file in os.listdir(picture1_src):
                shutil.copy2(
                    os.path.join(picture1_src, file),
                    os.path.join(picture1_dst, file)
                )
        
        # 复制图片2
        picture2_src = os.path.join(source_path, 'picture2')
        picture2_dst = os.path.join(storage_base, current_app.config['DATASET_PICTURE2_FOLDER'])
        if os.path.exists(picture2_src):
            for file in os.listdir(picture2_src):
                shutil.copy2(
                    os.path.join(picture2_src, file),
                    os.path.join(picture2_dst, file)
                )
                
        # 复制卫星数据文件夹（如果存在）
        satellite_src = os.path.join(source_path, 'satellite')
        satellite_dst = os.path.join(storage_base, 'satellite')
        if os.path.exists(satellite_src):
            # 确保目标目录存在
            os.makedirs(satellite_dst, exist_ok=True)
            for item in os.listdir(satellite_src):
                s = os.path.join(satellite_src, item)
                d = os.path.join(satellite_dst, item)
                if os.path.isdir(s):
                    shutil.copytree(s, d)
                else:
                    shutil.copy2(s, d)
    
    @staticmethod
    def _update_file_paths(dataset_detail, dataset_uuid):
        """
        更新数据集详情中的文件路径
        :param dataset_detail: 数据集详情对象
        :param dataset_uuid: 数据集UUID
        """
        # 查找并更新图片1路径
        picture1_folder = os.path.join(
            current_app.config['STORAGE_FOLDER'],
            current_app.config['DATASET_FOLDER'],
            dataset_uuid,
            current_app.config['DATASET_PICTURE1_FOLDER']
        )
        if os.path.exists(picture1_folder):
            files = os.listdir(picture1_folder)
            if files:
                dataset_detail.picture1_path = os.path.join(
                    current_app.config['DATASET_FOLDER'],
                    dataset_uuid,
                    current_app.config['DATASET_PICTURE1_FOLDER'],
                    files[0]
                )
        
        # 查找并更新图片2路径
        picture2_folder = os.path.join(
            current_app.config['STORAGE_FOLDER'],
            current_app.config['DATASET_FOLDER'],
            dataset_uuid,
            current_app.config['DATASET_PICTURE2_FOLDER']
        )
        if os.path.exists(picture2_folder):
            files = os.listdir(picture2_folder)
            if files:
                dataset_detail.picture2_path = os.path.join(
                    current_app.config['DATASET_FOLDER'],
                    dataset_uuid,
                    current_app.config['DATASET_PICTURE2_FOLDER'],
                    files[0]
                )
        
        # 更新输入文件夹路径
        input_path = os.path.join(
            current_app.config['DATASET_FOLDER'],
            dataset_uuid,
            current_app.config['DATASET_INPUT_FOLDER']
        )
        dataset_detail.input_path = input_path 