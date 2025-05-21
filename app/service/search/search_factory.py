"""
搜索工厂
"""
from typing import Dict, Type
from app.service.search.base_search_strategy import BaseSearchStrategy
from app.service.search.model_search_strategies import (
    ModelNameSearchStrategy,
    ModelOutputSearchStrategy,
    ModelCategorySearchStrategy,
    ModelScenarioSearchStrategy,
    ModelFuzzySearchStrategy,
    ModelTaskTypeSearchStrategy
)
from app.service.search.dataset_search_strategies import (
    DatasetCategorySearchStrategy,
    DatasetScenarioSearchStrategy,
    DatasetLocationSearchStrategy,
    DatasetFuzzySearchStrategy,
    DatasetModelNameSearchStrategy
)
from app.service.search.evaluate_search_strategies import (
    EvaluateTypeSearchStrategy,
    EvaluateModelNameSearchStrategy,
    EvaluateDatasetNameSearchStrategy,
    EvaluateStatusSearchStrategy
)

class SearchFactory:
    """搜索工厂类"""
    
    def __init__(self):
        self._strategies: Dict[str, Type[BaseSearchStrategy]] = {}
    
    def register_strategy(self, strategy_class: Type[BaseSearchStrategy], prefix: str):
        """
        注册搜索策略
        :param strategy_class: 策略类
        :param prefix: 策略前缀
        """
        strategy = strategy_class()
        self._strategies[f"{prefix}_{strategy.strategy_name}"] = strategy_class
    
    def get_strategy(self, strategy_name: str) -> BaseSearchStrategy:
        """
        获取搜索策略
        :param strategy_name: 策略名称
        :return: 搜索策略实例
        """
        strategy_class = self._strategies.get(strategy_name)
        if not strategy_class:
            raise ValueError(f"未找到名为 '{strategy_name}' 的搜索策略")
        return strategy_class()
    
    def get_all_strategy_names(self):
        """
        获取所有已注册的策略名称
        :return: 策略名称列表
        """
        return list(self._strategies.keys())

# 创建全局搜索工厂实例
search_factory = SearchFactory()

# 注册模型搜索策略
search_factory.register_strategy(ModelNameSearchStrategy, "model")
search_factory.register_strategy(ModelOutputSearchStrategy, "model")
search_factory.register_strategy(ModelCategorySearchStrategy, "model")
search_factory.register_strategy(ModelScenarioSearchStrategy, "model")
search_factory.register_strategy(ModelFuzzySearchStrategy, "model")
search_factory.register_strategy(ModelTaskTypeSearchStrategy, "model")

# 注册数据集搜索策略
search_factory.register_strategy(DatasetCategorySearchStrategy, "dataset")
search_factory.register_strategy(DatasetScenarioSearchStrategy, "dataset")
search_factory.register_strategy(DatasetLocationSearchStrategy, "dataset")
search_factory.register_strategy(DatasetFuzzySearchStrategy, "dataset")
search_factory.register_strategy(DatasetModelNameSearchStrategy, "dataset")

# 注册验证任务搜索策略
search_factory.register_strategy(EvaluateTypeSearchStrategy, "evaluate")
search_factory.register_strategy(EvaluateModelNameSearchStrategy, "evaluate")
search_factory.register_strategy(EvaluateDatasetNameSearchStrategy, "evaluate")
search_factory.register_strategy(EvaluateStatusSearchStrategy, "evaluate") 