"""
模型搜索策略
"""
from sqlalchemy import or_
from app.service.search.base_search_strategy import BaseSearchStrategy
from app.model.model_info import ModelInfo
from app.model.model_detail import ModelDetail

class ModelNameSearchStrategy(BaseSearchStrategy):
    """按模型名称搜索"""
    
    def apply(self, query, search_term):
        return query.filter(ModelInfo.name.ilike(f'%{search_term}%'))
    
    @property
    def strategy_name(self):
        return 'name'

class ModelOutputSearchStrategy(BaseSearchStrategy):
    """按模型输出搜索"""
    
    def apply(self, query, search_term):
        return query.filter(ModelInfo.output_type.ilike(f'%{search_term}%'))
    
    @property
    def strategy_name(self):
        return 'output'

class ModelCategorySearchStrategy(BaseSearchStrategy):
    """按模型类别搜索"""
    
    def apply(self, query, search_term):
        return query.filter(ModelInfo.model_category.ilike(f'%{search_term}%'))
    
    @property
    def strategy_name(self):
        return 'category'

class ModelScenarioSearchStrategy(BaseSearchStrategy):
    """按应用场景搜索"""
    
    def apply(self, query, search_term):
        return query.filter(ModelInfo.application_scenario.ilike(f'%{search_term}%'))
    
    @property
    def strategy_name(self):
        return 'scenario'

class ModelFuzzySearchStrategy(BaseSearchStrategy):
    """多字段模糊搜索"""
    
    def apply(self, query, search_term):
        """
        应用模糊搜索策略
        :param query: 基础查询对象
        :param search_term: 搜索关键词
        :return: 更新后的查询对象
        """
        # 使用 left join 确保即使没有详情记录也能返回结果
        return query.outerjoin(
            ModelDetail,
            ModelInfo.uuid == ModelDetail.model_uuid
        ).filter(
            or_(
                ModelInfo.name.ilike(f'%{search_term}%'),
                ModelInfo.output_type.ilike(f'%{search_term}%'),
                ModelInfo.model_category.ilike(f'%{search_term}%'),
                ModelInfo.application_scenario.ilike(f'%{search_term}%'),
                ModelInfo.parameter_count.ilike(f'%{search_term}%'),
                ModelInfo.convergence_time.ilike(f'%{search_term}%'),
                ModelDetail.description.ilike(f'%{search_term}%')
            )
        )
    
    @property
    def strategy_name(self):
        return 'fuzzy'

class ModelTaskTypeSearchStrategy(BaseSearchStrategy):
    """按模型任务类型搜索"""
    
    def apply(self, query, search_term):
        """
        应用任务类型搜索策略
        :param query: 基础查询对象
        :param search_term: 搜索关键词（任务类型数字1-4）
        :return: 更新后的查询对象
        """
        try:
            task_type = int(search_term)
            if 1 <= task_type <= 4:
                return query.filter(ModelInfo.task_type == task_type)
            return query.filter(False)  # 如果任务类型不在有效范围内，返回空结果
        except ValueError:
            return query.filter(False)  # 如果转换失败，返回空结果
    
    @property
    def strategy_name(self):
        return 'task_type' 