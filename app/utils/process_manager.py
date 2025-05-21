"""
进程管理器
用于管理异步执行的子进程
"""
import os
import subprocess
import threading
import queue
from typing import Dict, Optional, Callable
from datetime import datetime
from flask import current_app
from app import db
from app.model.evaluate_info import EvaluateInfo, EvaluateStatusType

class ProcessManager:
    """
    进程管理器单例类
    用于管理所有异步执行的子进程
    """
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(ProcessManager, cls).__new__(cls)
            return cls._instance
    
    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.processes: Dict[str, Dict] = {}
            self.initialized = True
    
    def get_max_processes(self) -> int:
        """
        获取最大进程数
        
        Returns:
            int: 最大进程数
        """
        return current_app.config['MAX_PROCESSES']
    
    def get_running_process_count(self) -> int:
        """
        获取当前运行的进程数
        
        Returns:
            int: 运行中的进程数
        """
        return sum(1 for info in self.processes.values() if info['status'] == 'running')
    
    def _read_output(self, pipe, output_queue):
        """
        读取进程输出的线程函数
        
        Args:
            pipe: 进程的输出管道
            output_queue: 用于存储输出的队列
        """
        try:
            for line in iter(pipe.readline, ''):
                output_queue.put(line.strip())
        except Exception as e:
            print(f"读取进程输出时发生错误: {str(e)}")
        finally:
            pipe.close()
    
    def start_process(self, process_id: str, cmd: list, cwd: str, env: dict, 
                     on_complete: Callable[[str, int], None] = None) -> bool:
        """
        启动一个新的子进程
        
        Args:
            process_id: 进程ID
            cmd: 要执行的命令
            cwd: 工作目录
            env: 环境变量
            on_complete: 进程结束时的回调函数，接收进程ID和返回码作为参数
            
        Returns:
            bool: 是否成功启动
        """
        try:
            # 检查是否达到最大进程数
            if self.get_running_process_count() >= self.get_max_processes():
                print(f"已达到最大进程数限制 ({self.get_max_processes()})")
                return False
            
            # 创建进程
            process = subprocess.Popen(
                cmd,
                cwd=cwd,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,  # 设置缓冲区大小为1
                creationflags=subprocess.CREATE_NO_WINDOW  # Windows下隐藏控制台窗口
            )
            
            # 创建输出队列
            stdout_queue = queue.Queue()
            stderr_queue = queue.Queue()
            
            # 记录进程信息
            self.processes[process_id] = {
                'process': process,
                'start_time': datetime.now(),
                'status': 'running',
                'cmd': cmd,
                'cwd': cwd,
                'on_complete': on_complete,
                'stdout_queue': stdout_queue,
                'stderr_queue': stderr_queue,
                'stdout_buffer': [],
                'stderr_buffer': []
            }
            
            # 启动输出读取线程
            stdout_thread = threading.Thread(
                target=self._read_output,
                args=(process.stdout, stdout_queue),
                daemon=True
            )
            stderr_thread = threading.Thread(
                target=self._read_output,
                args=(process.stderr, stderr_queue),
                daemon=True
            )
            stdout_thread.start()
            stderr_thread.start()
            
            # 启动监控线程
            self._monitor_process(process_id)
            
            return True
            
        except Exception as e:
            print(f"启动进程失败: {str(e)}")
            return False
    
    def stop_process(self, process_id: str) -> bool:
        """
        停止指定的进程
        
        Args:
            process_id: 进程ID
            
        Returns:
            bool: 是否成功停止
        """
        if process_id not in self.processes:
            return False
            
        try:
            process_info = self.processes[process_id]
            process = process_info['process']
            
            # 终止进程
            process.terminate()
            process_info['status'] = 'stopped'
            process_info['end_time'] = datetime.now()
            
            return True
            
        except Exception as e:
            print(f"停止进程失败: {str(e)}")
            return False
    
    def get_process_status(self, process_id: str) -> Optional[Dict]:
        """
        获取进程状态
        
        Args:
            process_id: 进程ID
            
        Returns:
            Dict: 进程状态信息，如果进程不存在则返回None
        """
        if process_id not in self.processes:
            return None
            
        process_info = self.processes[process_id]
        process = process_info['process']
        
        # 非阻塞读取输出
        try:
            # 读取stdout
            while True:
                try:
                    line = process_info['stdout_queue'].get_nowait()
                    process_info['stdout_buffer'].append(line)
                except queue.Empty:
                    break
                    
            # 读取stderr
            while True:
                try:
                    line = process_info['stderr_queue'].get_nowait()
                    process_info['stderr_buffer'].append(line)
                except queue.Empty:
                    break
                    
        except Exception as e:
            print(f"读取进程输出时发生错误: {str(e)}")
            
        return {
            'process_id': process_id,
            'status': process_info['status'],
            'start_time': process_info['start_time'].isoformat(),
            'end_time': process_info.get('end_time', '').isoformat() if 'end_time' in process_info else '',
            'return_code': process.returncode,
            'stdout': '\n'.join(process_info['stdout_buffer']),
            'stderr': '\n'.join(process_info['stderr_buffer']),
            'running_count': self.get_running_process_count(),
            'max_processes': self.get_max_processes()
        }
    
    def _monitor_process(self, process_id: str):
        """
        监控进程状态的线程函数
        
        Args:
            process_id: 进程ID
        """
        def monitor():
            process_info = self.processes[process_id]
            process = process_info['process']
            
            # 等待进程结束
            process.wait()
            
            # 更新进程状态
            process_info['status'] = 'completed'
            process_info['end_time'] = datetime.now()
            
            # 获取最终输出
            try:
                while True:
                    try:
                        line = process_info['stdout_queue'].get_nowait()
                        process_info['stdout_buffer'].append(line)
                    except queue.Empty:
                        break
                        
                while True:
                    try:
                        line = process_info['stderr_queue'].get_nowait()
                        process_info['stderr_buffer'].append(line)
                    except queue.Empty:
                        break
            except Exception as e:
                print(f"获取最终输出时发生错误: {str(e)}")
            
            # 调用回调函数
            if process_info.get('on_complete'):
                try:
                    process_info['on_complete'](process_id, process.returncode)
                except Exception as e:
                    print(f"执行回调函数时发生错误: {str(e)}")
            
        # 启动监控线程
        thread = threading.Thread(target=monitor)
        thread.daemon = True
        thread.start() 