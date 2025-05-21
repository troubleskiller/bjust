"""
日志配置模块
"""
import logging
import os
from logging.handlers import RotatingFileHandler
from flask import current_app

def setup_logger(name: str) -> logging.Logger:
    """
    设置日志记录器
    @param name: 日志记录器名称
    @return: 配置好的日志记录器
    """
    # 创建日志记录器
    logger = logging.getLogger(name)
    
    # 设置日志级别
    log_level = getattr(logging, current_app.config['LOG_LEVEL'].upper())
    logger.setLevel(log_level)
    
    # 创建格式化器
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # 创建控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # 如果配置了日志路径，则添加文件处理器
    log_path = current_app.config['LOG_PATH']
    if log_path:
        try:
            # 确保日志目录存在
            log_dir = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                log_path
            )
            os.makedirs(log_dir, exist_ok=True)
            
            # 创建文件处理器
            file_handler = RotatingFileHandler(
                os.path.join(log_dir, f'{name}.log'),
                maxBytes=current_app.config['LOG_MAX_BYTES'],
                backupCount=current_app.config['LOG_BACKUP_COUNT'],
                encoding='utf-8'
            )
            file_handler.setLevel(log_level)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        except Exception as e:
            # 如果创建文件处理器失败，记录错误但继续使用控制台输出
            logger.error(f"创建日志文件处理器失败: {e}")
    
    return logger 