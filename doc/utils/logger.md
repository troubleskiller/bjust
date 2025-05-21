# 日志配置模块 (logger.py)

## 实现机制

日志配置模块提供了一个统一的日志记录器设置函数，支持同时输出到控制台和文件，并实现了以下关键机制：

1. **多目标日志输出**：同时支持控制台和文件两种输出方式
2. **自动文件轮转**：使用`RotatingFileHandler`实现日志文件大小限制和自动轮转
3. **异常容错处理**：文件处理器创建失败时自动降级为仅控制台输出
4. **基于Flask配置的动态参数**：从应用配置中读取日志级别和路径等参数

## 代码示例

```python
from app.utils.logger import setup_logger

# 在应用中创建一个日志记录器
logger = setup_logger('my_module')

# 使用日志记录器记录不同级别的日志
logger.debug('调试信息')
logger.info('一般信息')
logger.warning('警告信息')
logger.error('错误信息')
logger.critical('严重错误信息')
```

## 技术依赖

- **Python 版本**: 3.6+
- **Flask**: 2.0.0+
- **依赖模块**:
  - `logging`: Python标准库
  - `os`: Python标准库
  - `logging.handlers`: Python标准库
  - `flask.current_app`: Flask应用上下文

## 配置参数

必须在Flask应用配置中设置以下参数：

```python
# Flask应用配置示例
app.config['LOG_LEVEL'] = 'INFO'  # 日志级别: DEBUG, INFO, WARNING, ERROR, CRITICAL
app.config['LOG_PATH'] = 'logs'   # 相对于项目根目录的日志文件存储路径
app.config['LOG_MAX_BYTES'] = 10485760  # 单个日志文件最大大小（字节）, 默认10MB
app.config['LOG_BACKUP_COUNT'] = 5     # 保留的备份日志文件数量
```

## 执行流程

1. **初始化**：调用`setup_logger`函数，传入日志记录器名称
2. **配置读取**：从Flask应用配置中读取LOG_LEVEL等参数
3. **日志级别设置**：将配置的日志级别字符串转换为logging模块的常量
4. **处理器创建**：
   - 创建并添加控制台处理器
   - 如果配置了日志路径，创建目录结构并添加文件处理器
5. **异常处理**：如果文件处理器创建失败，记录错误但继续使用控制台输出
6. **返回配置好的日志记录器**

## 数据流向

```
应用代码 -> setup_logger函数 -> 获取Flask配置 -> 创建日志记录器 -> 配置格式和处理器 -> 返回日志记录器 -> 应用代码使用日志记录器
```

## 实际使用场景

该日志模块在以下场景中特别有用：

1. **API服务器**：记录请求和响应信息
2. **后台处理服务**：记录任务执行状态和错误
3. **文件操作工具**：记录文件处理过程中的关键步骤和错误

例如，在文件解压服务中的应用：

```python
# 在safe_extractor.py中使用日志
class SafeExtractor:
    def __init__(self, zip_path, dest_path):
        self.logger = setup_logger('safe_extractor')
        self.logger.info(f"初始化解压器: {zip_path} -> {dest_path}")
        
    def extract_all(self):
        try:
            # 执行解压
            self.logger.info("开始解压文件...")
            # ...解压逻辑...
            self.logger.info("文件解压完成")
            return True
        except Exception as e:
            self.logger.error(f"解压过程发生错误: {e}")
            return False
```