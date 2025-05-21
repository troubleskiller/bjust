"""
数据集搜索策略
"""
from sqlalchemy import or_
from app.service.search.base_search_strategy import BaseSearchStrategy
from app.model.dataset_info import DatasetInfo
from app.model.dataset_detail import DatasetDetail

class DatasetCategorySearchStrategy(BaseSearchStrategy):
    """按数据集类别搜索"""
    
    def apply(self, query, search_term):
        return query.filter(DatasetInfo.category.ilike(f'%{search_term}%'))
    
    @property
    def strategy_name(self):
        return 'category'

class DatasetScenarioSearchStrategy(BaseSearchStrategy):
    """按数据集场景搜索"""
    
    def apply(self, query, search_term):
        return query.filter(DatasetInfo.scenario.ilike(f'%{search_term}%'))
    
    @property
    def strategy_name(self):
        return 'scenario'

class DatasetLocationSearchStrategy(BaseSearchStrategy):
    """按数据集地点搜索"""
    
    def apply(self, query, search_term):
        return query.filter(DatasetInfo.location.ilike(f'%{search_term}%'))
    
    @property
    def strategy_name(self):
        return 'location'

class DatasetFuzzySearchStrategy(BaseSearchStrategy):
    """多字段模糊搜索"""
    
    def apply(self, query, search_term):
        return query.join(DatasetDetail).filter(
            or_(
                DatasetInfo.category.ilike(f'%{search_term}%'),
                DatasetInfo.scenario.ilike(f'%{search_term}%'),
                DatasetInfo.location.ilike(f'%{search_term}%'),
                DatasetInfo.center_frequency.ilike(f'%{search_term}%'),
                DatasetInfo.bandwidth.ilike(f'%{search_term}%'),
                DatasetInfo.data_group_count.ilike(f'%{search_term}%'),
                DatasetInfo.applicable_models.ilike(f'%{search_term}%'),
                DatasetDetail.description.ilike(f'%{search_term}%')
            )
        )
    
    @property
    def strategy_name(self):
        return 'fuzzy'

class DatasetModelNameSearchStrategy(BaseSearchStrategy):
    """按适用模型名称搜索数据集"""
    
    def apply(self, query, search_term):
        """
        应用模型名称搜索策略
        :param query: 基础查询对象
        :param search_term: 搜索关键词（模型名称）
        :return: 更新后的查询对象
        """
        # 使用 LIKE 操作符进行精确匹配
        # 匹配模式：
        # 1. 完全匹配：model1
        # 2. 开头匹配：model1,
        # 3. 中间匹配：,model1,
        # 4. 结尾匹配：,model1
        pattern = f"%{search_term}%"
        return query.filter(
            or_(
                DatasetInfo.applicable_models == search_term,  # 完全匹配
                DatasetInfo.applicable_models.like(f"{search_term},%"),  # 开头匹配
                DatasetInfo.applicable_models.like(f"%,{search_term},%"),  # 中间匹配
                DatasetInfo.applicable_models.like(f"%,{search_term}")  # 结尾匹配
            )
        )
    
    @property
    def strategy_name(self):
        return 'model_name' 