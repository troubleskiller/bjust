"""
验证任务结果处理服务
"""
import os
import pandas as pd
import re
import time
from typing import Dict, List, Optional, Union, Tuple
from app import db
from app.model.evaluate_info import EvaluateInfo
from app.model.dataset_info import DatasetInfo
from flask import current_app

class EvaluateResultService:
    """验证任务结果处理服务类"""
    
    @staticmethod
    def get_evaluate_latest_result(evaluate_uuid: str, index: Optional[int] = None) -> Dict:
        """
        获取验证任务的最新结果
        :param evaluate_uuid: 验证任务UUID
        :param index: 可选参数，指定要获取数据的序号（从0开始）
        :return: 验证结果字典
        """
        # 获取验证任务信息
        evaluate = EvaluateInfo.query.get_or_404(evaluate_uuid)
        
        # 根据验证任务类型调用不同的处理方法
        if evaluate.evaluate_type == 1:
            return EvaluateResultService._process_type1_result(evaluate, index)
        elif evaluate.evaluate_type == 2:
            return EvaluateResultService._process_type2_result(evaluate, index)
        elif evaluate.evaluate_type == 3:
            return EvaluateResultService._process_type3_result(evaluate, index)
        elif evaluate.evaluate_type == 4:
            return EvaluateResultService._process_type4_result(evaluate, index)
        # TODO: 其他类型的处理逻辑将在后续实现
        return {}
    
    @staticmethod
    def _process_type1_result(evaluate: EvaluateInfo, index: Optional[int] = None) -> Dict:
        """
        处理类型1的验证结果
        :param evaluate: 验证任务对象
        :param index: 可选参数，指定要获取数据的序号（从0开始）
        :return: 处理结果字典
        """
        result = {
            'measure': [],
            'predict': [],
            'rmse': [],
            'satellite_path': None,
            'current_index': 0,  # 当前返回的数据的index
            'latest_index': 0    # 目前有效的最新的index
        }
        
        try:
            # 获取输出文件路径
            output_file = os.path.join(
                current_app.config['STORAGE_FOLDER'],
                current_app.config['EVALUATE_FOLDER'],
                evaluate.uuid,
                current_app.config['EVALUATE_OUTPUT_FOLDER'],
                'pathloss_result.csv'
            )
            
            # 检查文件是否存在
            if not os.path.exists(output_file):
                return result
                
            # 读取CSV文件，最多重试3次
            max_retries = 3
            retry_count = 0
            df = None
            
            while retry_count < max_retries:
                try:
                    df = pd.read_csv(output_file, header=None, names=['measure', 'predict', 'rmse'])
                    if not df.empty:
                        break
                except Exception as e:
                    current_app.logger.warning(f"第{retry_count + 1}次读取CSV文件失败: {str(e)}")
                    retry_count += 1
                    if retry_count < max_retries:
                        time.sleep(0.3)  # 等待0.3秒后重试
            
            if df is None or df.empty:
                print(df)
                current_app.logger.error(f"读取CSV文件失败，已重试{max_retries}次")
                return result
            
            # 找到第一个全零行
            last_row_index = -1
            for index_row, row in df.iterrows():
                if row['measure'] == 0 and row['predict'] == 0 and row['rmse'] == 0:
                    last_row_index = index_row
                    break
            
            # 如果找到全零行，只取到该行之前的数据
            if last_row_index != -1:
                df = df.iloc[:last_row_index]
                last_row_index = last_row_index - 1
            
            # 设置latest_index
            result['latest_index'] = last_row_index
            
            # 处理用户请求的index
            target_index = index if index is not None else last_row_index
            
            # 检查index是否合法
            if target_index < 0:
                # 小于0则返回能找到的第一组数据
                target_index = 0
            elif target_index > last_row_index:
                # 大于最大序号则返回最后一组数据
                target_index = last_row_index
            
            # 设置current_index
            result['current_index'] = target_index
            
            # 将数据转换为列表，只取到用户请求的index
            result['measure'] = df['measure'].iloc[:target_index+1].tolist()
            result['predict'] = df['predict'].iloc[:target_index+1].tolist()
            result['rmse'] = df['rmse'].iloc[:target_index+1].tolist()
            
            # 获取对应的卫星图片路径
            if evaluate.dataset_uuid and target_index != -1:
                satellite_path = os.path.join(
                    current_app.config['DATASET_FOLDER'],
                    evaluate.dataset_uuid,
                    'satellite',
                    f'{target_index}.png'
                )
                # 检查文件是否存在
                if os.path.exists(os.path.join(current_app.config['STORAGE_FOLDER'], satellite_path)):
                    result['satellite_path'] = satellite_path
            
        except Exception as e:
            current_app.logger.error(f"处理类型1验证结果时发生错误: {str(e)}")
        
        return result
    
    @staticmethod
    def _process_type2_result(evaluate: EvaluateInfo, index: Optional[int] = None) -> Dict:
        """
        处理类型2的验证结果
        :param evaluate: 验证任务对象
        :param index: 可选参数，指定要获取数据的序号（从0开始）
        :return: 处理结果字典
        """
        result = {
            'elevation_matrix': [],
            'pl_matrix': [],
            'satellite_path': None,
            'current_index': 0,  # 当前返回的数据的index
            'latest_index': 0    # 目前有效的最新的index
        }
        
        try:
            # 获取输出目录路径
            output_dir = os.path.join(
                current_app.config['STORAGE_FOLDER'],
                current_app.config['EVALUATE_FOLDER'],
                evaluate.uuid,
                current_app.config['EVALUATE_OUTPUT_FOLDER']
            )

            # 检查输出目录是否存在
            if not os.path.exists(output_dir):
                return result
            
            # 获取elevation_output和pl_output目录路径
            elevation_dir = os.path.join(output_dir, 'elevation_output')
            pl_dir = os.path.join(output_dir, 'pl_output')
            # 检查必要的目录是否存在
            if not all(os.path.exists(d) for d in [elevation_dir, pl_dir]):
                return result
            
            # 获取elevation_output目录下的所有文件
            elevation_files = [f for f in os.listdir(elevation_dir) 
                             if f.endswith('_elevation.csv')]
            if not elevation_files:
                return result

            # 提取所有文件中的数字并排序
            file_indices = []
            for file in elevation_files:
                match = re.search(r'.*?(\d+)_elevation\.csv$', file)
                if match:
                    file_indices.append((int(match.group(1)), file))
            
            # 按序号排序
            file_indices.sort(key=lambda x: x[0])
            
            if not file_indices:
                return result
            
            # 设置latest_index（文件列表中的最大序号）
            result['latest_index'] = len(file_indices) - 1
            
            # 处理用户请求的index
            target_index = index if index is not None else result['latest_index']
            
            # 检查index是否合法
            if target_index < 0:
                # 小于0则返回能找到的第一组数据
                target_index = 0
            elif target_index > result['latest_index']:
                # 大于最大序号则返回最后一组数据
                target_index = result['latest_index']
            
            # 设置current_index
            result['current_index'] = target_index
            
            # 获取目标文件
            if target_index < len(file_indices):
                # 获取对应的elevation文件
                _, elevation_file = file_indices[target_index]
                
                # 获取对应的path_loss文件
                pl_file = None
                for file in os.listdir(pl_dir):
                    if file.endswith(f'{file_indices[target_index][0]}_path_loss.csv'):
                        pl_file = file
                        break
                
                if not pl_file:
                    return result
                    
                # 检查卫星图片是否存在
                satellite_path = None
                if evaluate.dataset_uuid:
                    satellite_path = os.path.join(
                        current_app.config['DATASET_FOLDER'],
                        evaluate.dataset_uuid,
                        'satellite',
                        f'{target_index}.png'
                    )
                    if not os.path.exists(os.path.join(current_app.config['STORAGE_FOLDER'], satellite_path)):
                        satellite_path = None
                
                # 读取elevation文件
                elevation_path = os.path.join(elevation_dir, elevation_file)
                try:
                    # 使用pandas读取CSV文件，最多重试3次
                    max_retries = 3
                    retry_count = 0
                    df_elevation = None
                    
                    while retry_count < max_retries:
                        try:
                            df_elevation = pd.read_csv(elevation_path, header=None)
                            if not df_elevation.empty:
                                break
                        except Exception as e:
                            current_app.logger.warning(f"第{retry_count + 1}次读取elevation CSV文件失败: {str(e)}")
                            retry_count += 1
                            if retry_count < max_retries:
                                time.sleep(0.3)  # 等待0.3秒后重试
                    
                    if df_elevation is None or df_elevation.empty:
                        current_app.logger.error(f"读取elevation CSV文件失败，已重试{max_retries}次")
                        return result
                    
                    # 将DataFrame转换为二维列表
                    elevation_data = df_elevation.values.tolist()
                except Exception as e:
                    current_app.logger.warning(f"读取elevation文件失败: {str(e)}")
                    return result
                
                # 读取path_loss文件
                pl_path = os.path.join(pl_dir, pl_file)
                try:
                    # 使用pandas读取CSV文件，最多重试3次
                    max_retries = 3
                    retry_count = 0
                    df_pl = None
                    
                    while retry_count < max_retries:
                        try:
                            df_pl = pd.read_csv(pl_path, header=None)
                            if not df_pl.empty:
                                break
                        except Exception as e:
                            current_app.logger.warning(f"第{retry_count + 1}次读取path_loss CSV文件失败: {str(e)}")
                            retry_count += 1
                            if retry_count < max_retries:
                                time.sleep(0.3)  # 等待0.3秒后重试
                    
                    if df_pl is None or df_pl.empty:
                        current_app.logger.error(f"读取path_loss CSV文件失败，已重试{max_retries}次")
                        return result
                    
                    # 将DataFrame转换为二维列表
                    pl_data = df_pl.values.tolist()
                except Exception as e:
                    current_app.logger.warning(f"读取path_loss文件失败: {str(e)}")
                    return result
                    
                # 检查数据维度是否匹配
                if len(elevation_data) != len(pl_data) or not all(len(row1) == len(row2) 
                    for row1, row2 in zip(elevation_data, pl_data)):
                    return result
                
                # 设置结果
                result['elevation_matrix'] = elevation_data
                result['pl_matrix'] = pl_data
                if satellite_path:
                    result['satellite_path'] = satellite_path
            
        except Exception as e:
            current_app.logger.error(f"处理类型2验证结果时发生错误: {str(e)}")
            
        return result
    
    @staticmethod
    def _process_type3_result(evaluate: EvaluateInfo, index: Optional[int] = None) -> Dict:
        """
        处理类型3的验证结果
        :param evaluate: 验证任务对象
        :param index: 可选参数，指定要获取数据的序号（从0开始）
        :return: 处理结果字典
        """
        result = {
            'left_up_path': None,
            'left_down_path': None,
            'right_up_path': None,
            'right_down_path': None,
            'current_index': 0,  # 当前返回的数据的index
            'latest_index': 0    # 目前有效的最新的index
        }
        
        try:
            # 获取输出目录路径
            output_dir = os.path.join(
                current_app.config['STORAGE_FOLDER'],
                current_app.config['EVALUATE_FOLDER'],
                evaluate.uuid,
                current_app.config['EVALUATE_OUTPUT_FOLDER']
            )
            
            # 检查输出目录是否存在
            if not os.path.exists(output_dir):
                return result
            
            # 处理左侧图片
            left_up_dir = os.path.join(output_dir, 'left_up')
            left_down_dir = os.path.join(output_dir, 'left_down')
            
            # 处理右侧图片
            right_up_dir = os.path.join(output_dir, 'right_up')
            right_down_dir = os.path.join(output_dir, 'right_down')
            
            # 处理右侧图片
            if os.path.exists(right_up_dir) and os.path.exists(right_down_dir):
                # 获取right_up目录下的所有图片
                right_up_files = [f for f in os.listdir(right_up_dir) 
                                if f.startswith('gen_0_') and f.endswith('_pdp.png')]
                
                if right_up_files:
                    # 提取序号并排序
                    file_indices = []
                    for file in right_up_files:
                        match = re.search(r'gen_0_(\d+)_pdp\.png', file)
                        if match:
                            file_indices.append((int(match.group(1)), file))
                    
                    # 按序号排序
                    file_indices.sort(key=lambda x: x[0])
                    
                    if file_indices:
                        # 设置latest_index（文件列表中的最大序号）
                        result['latest_index'] = len(file_indices) - 1
                        
                        # 处理用户请求的index
                        target_index = index if index is not None else result['latest_index']
                        
                        # 检查index是否合法
                        if target_index < 0:
                            # 小于0则返回能找到的第一组数据
                            target_index = 0
                        elif target_index > result['latest_index']:
                            # 大于最大序号则返回最后一组数据
                            target_index = result['latest_index']
                        
                        # 设置current_index
                        result['current_index'] = target_index
                        
                        # 获取目标文件
                        if target_index < len(file_indices):
                            # 获取对应的right_up文件
                            _, right_up_file = file_indices[target_index]
                            
                            # 获取对应的right_down文件
                            right_down_file = f'gen_1_{file_indices[target_index][0]}_pdp.png'
                            
                            # 检查文件是否存在
                            right_up_path = os.path.join(right_up_dir, right_up_file)
                            right_down_path = os.path.join(right_down_dir, right_down_file)
                            
                            if os.path.exists(right_up_path) and os.path.exists(right_down_path):
                                result['right_up_path'] = os.path.join(
                                    current_app.config['EVALUATE_FOLDER'],
                                    evaluate.uuid,
                                    current_app.config['EVALUATE_OUTPUT_FOLDER'],
                                    'right_up',
                                    right_up_file
                                )
                                result['right_down_path'] = os.path.join(
                                    current_app.config['EVALUATE_FOLDER'],
                                    evaluate.uuid,
                                    current_app.config['EVALUATE_OUTPUT_FOLDER'],
                                    'right_down',
                                    right_down_file
                                )
            
            # 处理左侧图片（这些图片通常只有一组）
            if os.path.exists(left_up_dir):
                # 获取left_up目录下的唯一图片
                left_up_files = [f for f in os.listdir(left_up_dir) if f.endswith('.png')]
                if left_up_files:
                    result['left_up_path'] = os.path.join(
                        current_app.config['EVALUATE_FOLDER'],
                        evaluate.uuid,
                        current_app.config['EVALUATE_OUTPUT_FOLDER'],
                        'left_up',
                        left_up_files[0]
                    )
            
            if os.path.exists(left_down_dir):
                # 获取left_down目录下的唯一图片
                left_down_files = [f for f in os.listdir(left_down_dir) if f.endswith('.png')]
                if left_down_files:
                    result['left_down_path'] = os.path.join(
                        current_app.config['EVALUATE_FOLDER'],
                        evaluate.uuid,
                        current_app.config['EVALUATE_OUTPUT_FOLDER'],
                        'left_down',
                        left_down_files[0]
                    )
            
        except Exception as e:
            current_app.logger.error(f"处理类型3验证结果时发生错误: {str(e)}")
            
        return result
    
    @staticmethod
    def _process_type4_result(evaluate: EvaluateInfo, index: Optional[int] = None) -> Dict:
        """
        处理类型4的验证结果
        :param evaluate: 验证任务对象
        :param index: 可选参数，指定要获取数据的序号（从0开始）
        :return: 处理结果字典
        """
        result = {
            'pdp_path': None,
            'pl_path': None,
            'sf_path': None,
            'current_index': 0,  # 当前返回的数据的index
            'latest_index': 0    # 目前有效的最新的index
        }
        
        try:
            # 获取输出目录路径
            output_dir = os.path.join(
                current_app.config['STORAGE_FOLDER'],
                current_app.config['EVALUATE_FOLDER'],
                evaluate.uuid,
                current_app.config['EVALUATE_OUTPUT_FOLDER']
            )
            
            # 检查输出目录是否存在
            if not os.path.exists(output_dir):
                return result
            
            # 获取pdp文件夹路径
            pdp_dir = os.path.join(output_dir, 'pdp')
            pl_dir = os.path.join(output_dir, 'pl')
            sf_dir = os.path.join(output_dir, 'sf')
            
            # 检查所有必要的文件夹是否存在
            if not all(os.path.exists(d) for d in [pdp_dir, pl_dir, sf_dir]):
                return result
            
            # 获取pdp文件夹中的所有图片
            pdp_files = [f for f in os.listdir(pdp_dir) 
                        if f.startswith('3d_surface_plot_') and f.endswith('.png')]
            
            if not pdp_files:
                return result
            
            # 提取序号并排序
            file_indices = []
            for file in pdp_files:
                match = re.search(r'3d_surface_plot_(\d+)\.png', file)
                if match:
                    file_indices.append((int(match.group(1)), file))
            
            # 按序号排序
            file_indices.sort(key=lambda x: x[0])
            
            if not file_indices:
                return result
            
            def find_complete_image_set(start_index: int) -> Tuple[bool, int, Optional[str], Optional[str], Optional[str]]:
                """
                从指定索引开始向前查找完整的图片组
                :param start_index: 开始查找的索引
                :return: (是否找到完整组, 找到的索引, pdp文件名, pl文件名, sf文件名)
                """
                current_idx = start_index
                while current_idx >= 0:
                    # 获取当前索引的pdp文件
                    if current_idx >= len(file_indices):
                        current_idx -= 1
                        continue
                        
                    pdp_index, pdp_file = file_indices[current_idx]
                    
                    # 查找对应的pl文件
                    pl_file = None
                    for file in os.listdir(pl_dir):
                        match = re.search(r'pl_(\d+)\.png', file)
                        if match and int(match.group(1)) == pdp_index:
                            pl_file = file
                            break
                    
                    # 查找对应的sf文件
                    sf_file = None
                    for file in os.listdir(sf_dir):
                        match = re.search(r'sf_(\d+)\.png', file)
                        if match and int(match.group(1)) == pdp_index:
                            sf_file = file
                            break
                    
                    # 检查是否找到完整的一组图片
                    if pdp_file and pl_file and sf_file:
                        # 检查文件是否都存在
                        pdp_path = os.path.join(pdp_dir, pdp_file)
                        pl_path = os.path.join(pl_dir, pl_file)
                        sf_path = os.path.join(sf_dir, sf_file)
                        if all(os.path.exists(p) for p in [pdp_path, pl_path, sf_path]):
                            return True, current_idx, pdp_file, pl_file, sf_file
                    
                    current_idx -= 1
                
                return False, -1, None, None, None
            
            # 查找最后一组完整的图片组
            found, latest_complete_index, _, _, _ = find_complete_image_set(len(file_indices) - 1)
            if not found:
                return result
                
            # 设置latest_index为最后一组完整图片的索引
            result['latest_index'] = latest_complete_index
            
            # 处理用户请求的index
            target_index = index if index is not None else latest_complete_index
            
            # 检查index是否合法
            if target_index < 0:
                # 小于0则返回能找到的第一组数据
                target_index = 0
            elif target_index > latest_complete_index:
                # 大于最大序号则返回最后一组数据
                target_index = latest_complete_index
            
            # 查找完整的图片组
            found, found_index, pdp_file, pl_file, sf_file = find_complete_image_set(target_index)
            
            if found:
                # 设置current_index为找到的完整图片组的索引
                result['current_index'] = found_index
                
                # 设置路径
                result['pdp_path'] = os.path.join(
                    current_app.config['EVALUATE_FOLDER'],
                    evaluate.uuid,
                    current_app.config['EVALUATE_OUTPUT_FOLDER'],
                    'pdp',
                    pdp_file
                )
                result['pl_path'] = os.path.join(
                    current_app.config['EVALUATE_FOLDER'],
                    evaluate.uuid,
                    current_app.config['EVALUATE_OUTPUT_FOLDER'],
                    'pl',
                    pl_file
                )
                result['sf_path'] = os.path.join(
                    current_app.config['EVALUATE_FOLDER'],
                    evaluate.uuid,
                    current_app.config['EVALUATE_OUTPUT_FOLDER'],
                    'sf',
                    sf_file
                )
            
        except Exception as e:
            current_app.logger.error(f"处理类型4验证结果时发生错误: {str(e)}")
            
        return result 