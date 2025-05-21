"""
开发测试相关API路由
"""
import os
import uuid
from http import HTTPStatus
from flask import Blueprint, request, jsonify
from app.utils.response import ServerResponse
from app.utils.process_manager import ProcessManager

# 创建蓝图
bp = Blueprint('dev', __name__)
# 获取进程管理器实例
process_manager = ProcessManager()

@bp.route('/test', methods=['GET'])
def test_endpoint():
    """
    测试接口
    用于开发测试和健康检查
    """
    try:
        return jsonify(
            ServerResponse.success(
                data={'message': '测试接口正常'},
                message='测试成功'
            ).model_dump()
        ), HTTPStatus.OK.value
        
    except Exception as e:
        return jsonify(
            ServerResponse.error(f"测试接口异常：{str(e)}", HTTPStatus.INTERNAL_SERVER_ERROR.value).model_dump()
        ), HTTPStatus.INTERNAL_SERVER_ERROR.value

@bp.route('/run_model', methods=['POST'])
def run_model():
    """
    异步执行模型训练任务
    通过subprocess执行命令行指令
    """
    try:
        # 检查是否达到最大进程数
        if process_manager.get_running_process_count() >= process_manager.get_max_processes():
            return jsonify(
                ServerResponse.error(
                    f"已达到最大进程数限制 ({process_manager.get_max_processes()})",
                    HTTPStatus.TOO_MANY_REQUESTS.value
                ).model_dump()
            ), HTTPStatus.TOO_MANY_REQUESTS.value
        
        # 生成唯一的进程ID
        process_id = str(uuid.uuid4())
        
        # 设置工作目录
        work_dir = r"D:\Data\Work\other\bjtu\task\task3\model-3\model_code"
        
        # 设置环境变量
        env = os.environ.copy()
        env["PATH"] = r"D:\Data\Work\other\bjtu\task\task3\model-3\model_python_env\Library\bin;" + env["PATH"]
        
        # 构建命令
        python_exe = r"D:\Data\Work\other\bjtu\task\task3\model-3\model_python_env\python.exe"
        script_path = r"D:\Data\Work\other\bjtu\task\task3\model-3\model_code\main.py"
        input_dir = r"D:\Data\Work\other\bjtu\task\task3\dataset-2对应任务3\input"
        output_dir = r"D:\Data\Work\other\bjtu\task\task3\output"
        
        cmd = [python_exe, script_path, input_dir, output_dir]
        
        # 启动进程
        if process_manager.start_process(process_id, cmd, work_dir, env):
            return jsonify(
                ServerResponse.success(
                    data={
                        'process_id': process_id,
                        'message': '模型任务已启动',
                        'running_count': process_manager.get_running_process_count(),
                        'max_processes': process_manager.get_max_processes()
                    },
                    message='任务启动成功'
                ).model_dump()
            ), HTTPStatus.OK.value
        else:
            return jsonify(
                ServerResponse.error(
                    "启动模型任务失败",
                    HTTPStatus.INTERNAL_SERVER_ERROR.value
                ).model_dump()
            ), HTTPStatus.INTERNAL_SERVER_ERROR.value
            
    except Exception as e:
        return jsonify(
            ServerResponse.error(f"启动模型任务时发生错误：{str(e)}", HTTPStatus.INTERNAL_SERVER_ERROR.value).model_dump()
        ), HTTPStatus.INTERNAL_SERVER_ERROR.value

@bp.route('/process/<process_id>/status', methods=['GET'])
def get_process_status(process_id):
    """
    获取指定进程的状态
    
    Args:
        process_id: 进程ID
    """
    try:
        status = process_manager.get_process_status(process_id)
        if status is None:
            return jsonify(
                ServerResponse.error(
                    "进程不存在",
                    HTTPStatus.NOT_FOUND.value
                ).model_dump()
            ), HTTPStatus.NOT_FOUND.value
            
        return jsonify(
            ServerResponse.success(
                data=status,
                message='获取进程状态成功'
            ).model_dump()
        ), HTTPStatus.OK.value
        
    except Exception as e:
        return jsonify(
            ServerResponse.error(f"获取进程状态时发生错误：{str(e)}", HTTPStatus.INTERNAL_SERVER_ERROR.value).model_dump()
        ), HTTPStatus.INTERNAL_SERVER_ERROR.value

@bp.route('/process/<process_id>/stop', methods=['POST'])
def stop_process(process_id):
    """
    停止指定的进程
    
    Args:
        process_id: 进程ID
    """
    try:
        if process_manager.stop_process(process_id):
            return jsonify(
                ServerResponse.success(
                    message='停止进程成功'
                ).model_dump()
            ), HTTPStatus.OK.value
        else:
            return jsonify(
                ServerResponse.error(
                    "进程不存在或停止失败",
                    HTTPStatus.NOT_FOUND.value
                ).model_dump()
            ), HTTPStatus.NOT_FOUND.value
            
    except Exception as e:
        return jsonify(
            ServerResponse.error(f"停止进程时发生错误：{str(e)}", HTTPStatus.INTERNAL_SERVER_ERROR.value).model_dump()
        ), HTTPStatus.INTERNAL_SERVER_ERROR.value

@bp.route('/process/config/max_processes', methods=['GET'])
def get_max_processes():
    """
    获取最大进程数限制
    """
    try:
        return jsonify(
            ServerResponse.success(
                data={
                    'max_processes': process_manager.get_max_processes(),
                    'running_count': process_manager.get_running_process_count()
                },
                message='获取成功'
            ).model_dump()
        ), HTTPStatus.OK.value
        
    except Exception as e:
        return jsonify(
            ServerResponse.error(f"获取最大进程数时发生错误：{str(e)}", HTTPStatus.INTERNAL_SERVER_ERROR.value).model_dump()
        ), HTTPStatus.INTERNAL_SERVER_ERROR.value 