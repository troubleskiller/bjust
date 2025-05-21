"""
统一的服务器响应模型
"""
from typing import TypeVar, Generic, Optional
from pydantic import BaseModel

T = TypeVar("T")

class ServerResponseBase(BaseModel):
    """服务器响应基类"""
    code: int
    message: str

    class Config:
        from_attributes = True

class ServerResponse(ServerResponseBase, Generic[T]):
    """
    通用服务器响应类
    :param T: 响应数据的类型
    """
    data: Optional[T] = None

    def __init__(self, code: int, message: str, data: Optional[T] = None):
        """
        初始化响应对象
        :param code: 响应码
        :param message: 响应消息
        :param data: 响应数据
        """
        super().__init__(code=code, message=message)
        self.data = data

    @staticmethod
    def success(data: Optional[T] = None, message: str = "操作成功") -> "ServerResponse[T]":
        """
        创建成功响应
        :param data: 响应数据
        :param message: 响应消息
        :return: 成功响应对象
        """
        return ServerResponse(code=200, message=message, data=data)

    @staticmethod
    def error(message: str = "操作失败", code: int = 500) -> "ServerResponse[T]":
        """
        创建错误响应
        :param message: 错误消息
        :param code: 错误码
        :return: 错误响应对象
        """
        return ServerResponse(code=code, message=message) 