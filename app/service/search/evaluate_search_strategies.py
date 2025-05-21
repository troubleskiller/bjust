"""
验证任务搜索策略
"""
from sqlalchemy import or_
from app.service.search.base_search_strategy import BaseSearchStrategy
from app.model.evaluate_info import EvaluateInfo, EvaluateStatusType
from app.model.model_info import ModelInfo
from app.model.dataset_info import DatasetInfo

class EvaluateTypeSearchStrategy(BaseSearchStrategy):
    """按验证任务类型搜索"""
    
    def apply(self, query, search_term):
        """
        应用类型搜索策略
        :param query: 原始查询对象
        :param search_term: 搜索关键词（任务类型数字）
        :return: 修改后的查询对象
        """
        try:
            evaluate_type = int(search_term)
            return query.filter(EvaluateInfo.evaluate_type == evaluate_type)
        except ValueError:
            return query.filter(False)  # 如果转换失败，返回空结果
    
    @property
    def strategy_name(self):
        return 'type'

class EvaluateModelNameSearchStrategy(BaseSearchStrategy):
    """按关联模型名称搜索"""
    
    def apply(self, query, search_term):
        """
        应用模型名称搜索策略
        :param query: 原始查询对象
        :param search_term: 搜索关键词（模型名称）
        :return: 修改后的查询对象
        """
        # 先查询符合条件的模型
        model_ids = [model.uuid for model in ModelInfo.query.filter(
            ModelInfo.name.ilike(f'%{search_term}%')
        ).all()]
        
        # 如果找到模型，则查询关联的验证任务
        if model_ids:
            return query.filter(EvaluateInfo.model_uuid.in_(model_ids))
        return query.filter(False)  # 如果没有找到模型，返回空结果
    
    @property
    def strategy_name(self):
        return 'model_name'

class EvaluateDatasetNameSearchStrategy(BaseSearchStrategy):
    """按关联数据集名称搜索"""
    
    def apply(self, query, search_term):
        """
        应用数据集名称搜索策略
        :param query: 原始查询对象
        :param search_term: 搜索关键词（数据集名称）
        :return: 修改后的查询对象
        """
        # 先查询符合条件的数据集
        dataset_ids = [dataset.uuid for dataset in DatasetInfo.query.filter(
            DatasetInfo.category.ilike(f'%{search_term}%')
        ).all()]
        
        # 如果找到数据集，则查询关联的验证任务
        if dataset_ids:
            return query.filter(EvaluateInfo.dataset_uuid.in_(dataset_ids))
        return query.filter(False)  # 如果没有找到数据集，返回空结果
    
    @property
    def strategy_name(self):
        return 'dataset_name'

class EvaluateStatusSearchStrategy(BaseSearchStrategy):
    """按验证任务状态搜索"""
    
    def apply(self, query, search_term):
        """
        应用状态搜索策略
        :param query: 原始查询对象
        :param search_term: 搜索关键词（状态名称）
        :return: 修改后的查询对象
        """
        # 查找匹配的状态值
        matching_status = None
        for status in EvaluateStatusType:
            if status.value == search_term:
                matching_status = status.value
                break
        
        if matching_status:
            return query.filter(EvaluateInfo.evaluate_status == matching_status)
        return query.filter(False)  # 如果没有找到匹配的状态，返回空结果
    
    @property
    def strategy_name(self):
        return 'status' 