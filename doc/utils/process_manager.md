# 进程管理器 (process_manager.py)

## 实现机制

进程管理器实现了一个单例模式的进程控制系统，用于管理异步执行的子进程，具有以下核心机制：

1. **单例模式**：使用线程安全的单例模式确保全局只有一个进程管理器实例
2. **多线程支持**：使用线程锁和队列实现线程安全的进程管理
3. **非阻塞输出捕获**：使用单独的线程读取进程的stdout和stderr，实现非阻塞的输出捕获
4. **进程并发控制**：支持设置最大进程数，防止过多进程导致系统资源耗尽
5. **进程生命周期管理**：支持进程的启动、监控和停止，并提供完成回调机制

## 代码示例

```python
from app.utils.process_manager import ProcessManager

# 获取进程管理器实例
process_manager = ProcessManager()

# 定义进程完成时的回调函数
def on_process_complete(process_id, return_code):
    print(f"进程 {process_id} 已完成，返回码: {return_code}")

# 启动一个新的进程
process_id = "unique_process_id"
cmd = ["python", "-c", "import time; print('Hello'); time.sleep(5); print('Goodbye')"]
working_dir = "/path/to/working/directory"
env_vars = {"PYTHONPATH": "/custom/python/path"}

success = process_manager.start_process(
    process_id=process_id,
    cmd=cmd,
    cwd=working_dir,
    env=env_vars,
    on_complete=on_process_complete
)

if success:
    print(f"进程 {process_id} 已启动")
else:
    print("启动进程失败，可能已达到最大进程数限制")

# 获取进程状态
status = process_manager.get_process_status(process_id)
print(f"进程状态: {status['status']}")
print(f"标准输出: {status['stdout']}")

# 停止进程
if process_manager.stop_process(process_id):
    print(f"进程 {process_id} 已停止")
else:
    print(f"停止进程 {process_id} 失败")
```

## 技术依赖

- **Python 版本**: 3.6+
- **依赖模块**:
  - `os`: Python标准库
  - `subprocess`: Python标准库
  - `threading`: Python标准库
  - `queue`: Python标准库
  - `datetime`: Python标准库
  - `flask.current_app`: Flask应用上下文

## 配置参数

进程管理器依赖于Flask应用配置中的以下参数：

```python
# Flask应用配置示例
app.config['MAX_PROCESSES'] = 5  # 同时运行的最大进程数
```

## 执行流程

### 进程启动流程

1. **参数验证**：检查当前运行的进程数是否已达到最大值
2. **进程创建**：使用`subprocess.Popen`创建新的子进程
3. **输出队列初始化**：为stdout和stderr创建队列
4. **进程信息记录**：记录进程信息，包括启动时间、命令、回调函数等
5. **输出读取线程启动**：启动两个后台线程，分别读取stdout和stderr
6. **监控线程启动**：启动一个后台线程监控进程状态

### 进程监控流程

1. **等待进程结束**：调用`process.wait()`阻塞等待进程结束
2. **更新进程状态**：进程结束后更新状态为completed
3. **获取最终输出**：从队列中读取所有剩余的输出
4. **执行回调函数**：调用用户提供的回调函数，传递进程ID和返回码

## 数据流向

```
应用代码 -> ProcessManager.start_process -> 创建子进程 -> 
启动输出读取线程(stdout, stderr) -> 
进程输出 -> 输出队列 -> ProcessManager.get_process_status -> 应用代码

进程结束 -> 监控线程检测到 -> 执行回调函数 -> 应用代码处理回调
```

## 实际使用场景

进程管理器在以下场景中特别有用：

1. **AI模型评估系统**：启动并监控多个模型评估进程
2. **数据处理管道**：运行多个数据处理子任务并收集结果
3. **后台任务系统**：管理用户触发的长时间运行的计算任务

下面是在模型评估服务中的实际应用示例：

```python
# 在evaluate_service.py中使用进程管理器
from app.utils.process_manager import ProcessManager

class EvaluateService:
    # 创建进程管理器实例
    _process_manager = ProcessManager()
    
    @classmethod
    def run_evaluate(cls, evaluate_uuid):
        # 获取模型和数据集信息
        evaluate = EvaluateInfo.query.get_or_404(evaluate_uuid)
        model = ModelInfo.query.get(evaluate.model_uuid)
        
        # 构建命令
        python_exe = "/path/to/python.exe"
        script_path = "/path/to/evaluation/script.py"
        cmd = [python_exe, script_path, input_dir, output_dir]
        
        # 更新任务状态为"进行中"
        evaluate.evaluate_status = EvaluateStatusType.IN_PROGRESS.value
        db.session.commit()
        
        # 启动进程
        if cls._process_manager.start_process(
            evaluate_uuid, 
            cmd, 
            work_dir, 
            env, 
            cls._on_process_complete
        ):
            return {"message": "验证任务已启动"}
        else:
            # 如果启动失败，恢复任务状态
            evaluate.evaluate_status = EvaluateStatusType.NOT_STARTED.value
            db.session.commit()
            raise RuntimeError("启动验证任务失败")
```

## 注意事项

1. **最大进程数限制**：确保设置合理的`MAX_PROCESSES`值，避免系统资源耗尽
2. **内存管理**：长时间运行可能导致输出缓冲区占用大量内存，应定期获取状态清空缓冲区
3. **进程实例清理**：在不需要监控的进程完成后，应从`processes`字典中移除相关条目
4. **Windows特定配置**：在Windows平台上使用`CREATE_NO_WINDOW`标志隐藏控制台窗口