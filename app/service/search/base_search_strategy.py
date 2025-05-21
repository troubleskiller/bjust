"""
搜索策略基类
"""
from abc import ABC, abstractmethod
from typing import Any
from sqlalchemy.orm import Query

class BaseSearchStrategy(ABC):
    """搜索策略基类"""
    
    @abstractmethod
    def apply(self, query: Query, search_term: str) -> Query:
        """
        应用搜索策略
        :param query: 原始查询对象
        :param search_term: 搜索关键词
        :return: 修改后的查询对象
        """
        pass
    
    @property
    @abstractmethod
    def strategy_name(self) -> str:
        """
        获取策略名称
        :return: 策略名称
        """
        pass 