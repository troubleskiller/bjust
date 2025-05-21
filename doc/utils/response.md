# 服务器响应模型 (response.py)

## 实现机制

服务器响应模型提供了一个统一的API响应格式，基于Pydantic实现，具有以下关键机制：

1. **泛型响应类型**：使用Python泛型（Generic）支持任意类型的响应数据
2. **类型化响应**：利用Pydantic的类型验证确保响应格式符合预期
3. **标准化响应格式**：统一的响应结构包含状态码、消息和数据三个主要部分
4. **工厂方法模式**：提供静态工厂方法快速创建成功和错误响应

## 代码示例

```python
from app.utils.response import ServerResponse
from pydantic import BaseModel
from typing import List

# 定义数据模型
class UserInfo(BaseModel):
    id: int
    name: str
    email: str

# 创建成功响应，包含单个对象
user = UserInfo(id=1, name="张三", email="zhangsan@example.com")
response = ServerResponse.success(data=user, message="获取用户成功")

# 创建成功响应，包含列表
users = [
    UserInfo(id=1, name="张三", email="zhangsan@example.com"),
    UserInfo(id=2, name="李四", email="lisi@example.com")
]
response = ServerResponse.success(data=users, message="获取用户列表成功")

# 创建错误响应
response = ServerResponse.error(message="用户不存在", code=404)

# 在Flask路由处理器中使用
@app.route('/api/users/<int:user_id>')
def get_user(user_id):
    try:
        user = User.query.get(user_id)
        if not user:
            return ServerResponse.error(message="用户不存在", code=404).dict()
        return ServerResponse.success(data=user.to_dict(), message="获取用户成功").dict()
    except Exception as e:
        return ServerResponse.error(message=f"获取用户失败: {str(e)}").dict()
```

## 技术依赖

- **Python 版本**: 3.7+（支持泛型类型变量）
- **依赖模块**:
  - `typing`: Python标准库，用于类型注解
  - `pydantic`: 1.8.0+，用于数据验证和序列化

## 配置参数

`ServerResponse`类不依赖外部配置，但有以下默认参数：

- **成功响应**:
  - `code`: 200
  - `message`: "操作成功"
- **错误响应**:
  - `code`: 500
  - `message`: "操作失败" 

## 响应格式

标准JSON响应格式为：

```json
{
  "code": 200,                  // 状态码：200成功，其他表示错误
  "message": "操作成功",         // 操作结果消息
  "data": {                     // 可选，响应数据对象
    "property1": "value1",
    "property2": "value2"
  }
}
```

## 执行流程

### 成功响应流程

1. **调用工厂方法**：通过`ServerResponse.success()`创建响应对象
2. **序列化数据**：Pydantic自动将数据序列化为兼容格式
3. **生成响应**：将成功状态码、消息和数据合并为响应对象

### 错误响应流程

1. **调用工厂方法**：通过`ServerResponse.error()`创建响应对象
2. **设置错误信息**：包含错误消息和状态码
3. **生成响应**：创建不包含数据字段的错误响应对象

## 数据流向

```
应用业务逻辑 -> 创建数据对象 -> ServerResponse.success/error -> 
Pydantic序列化 -> JSON响应 -> 客户端
```

## 使用技巧与最佳实践

1. **类型安全**：利用泛型参数提供类型安全的响应

```python
# 明确指定响应数据类型
response: ServerResponse[UserInfo] = ServerResponse.success(data=user)
```

2. **响应码规范**：遵循HTTP状态码标准

```python
# 常用错误码
NOT_FOUND = 404        # 资源不存在
BAD_REQUEST = 400      # 请求参数错误
UNAUTHORIZED = 401     # 未授权
FORBIDDEN = 403        # 禁止访问
SERVER_ERROR = 500     # 服务器内部错误

# 使用示例
response = ServerResponse.error(message="无权访问", code=FORBIDDEN)
```

3. **链式调用**：与其他方法组合使用

```python
# 条件响应示例
def get_user_response(user_id):
    user = find_user(user_id)
    return (
        ServerResponse.success(data=user.to_dict())
        if user else
        ServerResponse.error(message="用户不存在", code=404)
    )
```

## 实际使用场景

该响应模型在以下场景中特别有用：

1. **RESTful API**：提供统一的API响应格式
2. **微服务架构**：在服务间提供一致的通信格式
3. **前后端分离应用**：简化前端对响应格式的处理

以下是一个在评估服务API中的实际应用示例：

```python
# 在路由处理器中使用
@app.route('/api/evaluate/<uuid>', methods=['POST'])
def run_evaluate(uuid):
    try:
        # 调用评估服务
        result = EvaluateService.run_evaluate(uuid)
        return ServerResponse.success(data=result).dict()
    except ValueError as e:
        # 参数验证错误
        return ServerResponse.error(message=str(e), code=400).dict()
    except Exception as e:
        # 服务器错误
        app.logger.error(f"运行评估任务失败: {str(e)}")
        return ServerResponse.error(message="运行评估任务失败").dict()
```