"""
验证任务服务层
"""
from datetime import datetime
import os
import shutil
from typing import Dict
from app import db, create_app
from flask import current_app
from app.model.evaluate_info import EvaluateInfo, EvaluateStatusType
from app.model.model_info import ModelInfo
from app.model.model_detail import ModelDetail
from app.model.dataset_info import DatasetInfo
from app.model.dataset_detail import DatasetDetail
from app.service.search.search_factory import search_factory
from app.utils.process_manager import ProcessManager


class EvaluateService:
    """验证任务服务类"""

    # 创建进程管理器实例
    _process_manager = ProcessManager()

    # 用于存储应用实例
    _app = None

    @classmethod
    def _get_app(cls):
        """
        获取应用实例（单例模式）
        :return: Flask应用实例
        """
        if cls._app is None:
            cls._app = create_app()
        return cls._app

    @classmethod
    def _on_process_complete(cls, process_id: str, return_code: int):
        """
        进程结束时的回调函数
        :param process_id: 进程ID（验证任务UUID）
        :param return_code: 进程返回码
        """
        app = cls._get_app()
        try:
            with app.app_context():
                # 确保数据库连接
                if not db.engine:
                    db.init_app(app)

                # 获取验证任务
                evaluate = EvaluateInfo.query.get(process_id)
                if evaluate:
                    # 根据返回码设置状态
                    if return_code == 0:
                        evaluate.evaluate_status = EvaluateStatusType.COMPLETED.value
                    else:
                        evaluate.evaluate_status = EvaluateStatusType.ABORTED.value
                    # 设置结束时间
                    evaluate.end_time = datetime.utcnow()
                    db.session.commit()
        except Exception as e:
            # 记录错误日志
            app.logger.error(f"更新验证任务状态时发生错误: {str(e)}")
            # 确保数据库会话被回滚
            if 'db' in locals() and db.session:
                db.session.rollback()

    @classmethod
    def get_process_status(cls, evaluate_uuid: str) -> Dict:
        """
        获取验证任务进程状态
        :param evaluate_uuid: 验证任务UUID
        :return: 进程状态信息
        """
        try:
            # 获取验证任务
            evaluate = EvaluateInfo.query.get_or_404(evaluate_uuid)

            # 获取进程状态
            status = cls._process_manager.get_process_status(evaluate_uuid)
            if status is None:
                return {
                    'evaluate_uuid': evaluate_uuid,
                    'evaluate_status': evaluate.evaluate_status,
                    'start_time': evaluate.start_time.isoformat() if evaluate.start_time else None,
                    'end_time': evaluate.end_time.isoformat() if evaluate.end_time else None,
                    'message': '进程不存在'
                }

            return status

        except Exception as e:
            current_app.logger.error(f"获取验证任务进程状态时发生错误: {str(e)}")
            raise e

    @classmethod
    def stop_process(cls, evaluate_uuid: str) -> bool:
        """
        停止验证任务进程
        :param evaluate_uuid: 验证任务UUID
        :return: 是否成功停止
        """
        try:
            # 获取验证任务
            evaluate = EvaluateInfo.query.get_or_404(evaluate_uuid)

            # 获取进程状态
            process_status = cls._process_manager.get_process_status(evaluate_uuid)

            # 检查任务状态和进程状态
            if evaluate.evaluate_status != EvaluateStatusType.IN_PROGRESS.value and not process_status:
                raise ValueError("只能停止正在进行中的任务")

            # 停止进程
            process_stopped = cls._process_manager.stop_process(evaluate_uuid)

            # 无论进程是否存在，都更新任务状态
            evaluate.evaluate_status = EvaluateStatusType.ABORTED.value
            evaluate.end_time = datetime.utcnow()
            db.session.commit()

            return process_stopped

        except Exception as e:
            current_app.logger.error(f"停止验证任务进程时发生错误: {str(e)}")
            raise e

    @staticmethod
    def update_evaluate(evaluate_uuid: str, evaluate_type: int = None,
                        model_uuid: str = None, dataset_uuid: str = None,
                        extra_parameter: str = None) -> Dict:
        """
        更新验证任务信息
        :param evaluate_uuid: 验证任务UUID
        :param evaluate_type: 验证任务类型(1-4)（可选）
        :param model_uuid: 关联的模型UUID（可选）
        :param dataset_uuid: 关联的数据集UUID（可选）
        :param extra_parameter: 额外参数（可选）
        :return: 更新后的验证任务信息
        """
        try:
            # 获取验证任务
            evaluate = EvaluateInfo.query.get_or_404(evaluate_uuid)

            # 检查任务状态
            if evaluate.evaluate_status == EvaluateStatusType.IN_PROGRESS.value:
                raise ValueError("任务正在进行中，无法更新")

            # 检查是否有对应的进程
            process_status = EvaluateService._process_manager.get_process_status(evaluate_uuid)
            if process_status and process_status.get('status') == 'running':
                raise ValueError("任务正在运行中，无法更新")

            # 如果提供了evaluate_type，验证其有效性
            if evaluate_type is not None:
                if not isinstance(evaluate_type, int) or evaluate_type < 1 or evaluate_type > 4:
                    raise ValueError("验证任务类型必须是1-4之间的整数")
                evaluate.evaluate_type = evaluate_type

            # 如果提供了model_uuid，验证其存在性
            if model_uuid is not None:
                if model_uuid:  # 如果不是空字符串
                    model = ModelInfo.query.get(model_uuid)
                    if not model:
                        raise ValueError(f"未找到UUID为 {model_uuid} 的模型")
                evaluate.model_uuid = model_uuid

            # 如果提供了dataset_uuid，验证其存在性
            if dataset_uuid is not None:
                if dataset_uuid:  # 如果不是空字符串
                    dataset = DatasetInfo.query.get(dataset_uuid)
                    if not dataset:
                        raise ValueError(f"未找到UUID为 {dataset_uuid} 的数据集")
                evaluate.dataset_uuid = dataset_uuid

            # 如果提供了extra_parameter，更新它
            if extra_parameter is not None:
                evaluate.extra_parameter = extra_parameter

            # 保存到数据库
            db.session.commit()

            # 返回更新后的任务信息
            return evaluate.to_dict()

        except Exception as e:
            db.session.rollback()
            raise e

    @staticmethod
    def create_evaluate(evaluate_type: int = 1, model_uuid: str = None,
                        dataset_uuid: str = None, extra_parameter: str = None) -> Dict:
        """
        创建新的验证任务
        :param evaluate_type: 验证任务类型(1-4)，默认为1
        :param model_uuid: 关联的模型UUID（可选）
        :param dataset_uuid: 关联的数据集UUID（可选）
        :param extra_parameter: 额外参数（可选）
        :return: 创建的验证任务信息
        """
        try:
            # 验证任务类型
            if not isinstance(evaluate_type, int) or evaluate_type < 1 or evaluate_type > 4:
                raise ValueError("验证任务类型必须是1-4之间的整数")

            # 如果提供了model_uuid，验证其存在性
            if model_uuid:
                model = ModelInfo.query.get(model_uuid)
                if not model:
                    raise ValueError(f"未找到UUID为 {model_uuid} 的模型")

            # 如果提供了dataset_uuid，验证其存在性
            if dataset_uuid:
                dataset = DatasetInfo.query.get(dataset_uuid)
                if not dataset:
                    raise ValueError(f"未找到UUID为 {dataset_uuid} 的数据集")

            # 创建验证任务对象
            evaluate = EvaluateInfo(
                evaluate_type=evaluate_type,
                model_uuid=model_uuid,
                dataset_uuid=dataset_uuid,
                extra_parameter=extra_parameter,
                evaluate_status=EvaluateStatusType.NOT_STARTED.value,
                start_time=datetime.utcnow()
            )

            # 保存到数据库
            db.session.add(evaluate)
            db.session.commit()

            # 确保必要的文件夹存在
            evaluate.ensure_folders()

            # 返回创建的任务信息
            return evaluate.to_dict()

        except Exception as e:
            db.session.rollback()
            raise e

    @staticmethod
    def get_evaluate_list(page=1, per_page=10, search_type=None, search_term=None):
        """
        分页获取验证任务列表
        :param page: 页码（从1开始）
        :param per_page: 每页数量
        :param search_type: 搜索类型
        :param search_term: 搜索关键词
        :return: 验证任务列表和分页信息
        """
        # 创建基础查询
        query = EvaluateInfo.query

        # 如果指定了搜索类型和关键词，应用搜索策略
        if search_type and search_term:
            try:
                # 添加验证任务前缀
                strategy = search_factory.get_strategy(f"evaluate_{search_type}")
                query = strategy.apply(query, search_term)
            except ValueError as e:
                raise ValueError(f"搜索类型无效：{str(e)}")

        # 应用排序
        query = query.order_by(EvaluateInfo.start_time.desc())

        # 执行分页查询
        pagination = query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )

        # 获取当前页的数据
        items = []
        for evaluate in pagination.items:
            # 获取基础信息
            evaluate_dict = evaluate.to_dict()

            # 获取关联的模型名称
            if evaluate.model_uuid:
                model = ModelInfo.query.get(evaluate.model_uuid)
                evaluate_dict['model_name'] = model.name if model else None
            else:
                evaluate_dict['model_name'] = None

            # 获取关联的数据集名称
            if evaluate.dataset_uuid:
                dataset = DatasetInfo.query.get(evaluate.dataset_uuid)
                evaluate_dict[
                    'dataset_name'] = f"[{dataset.scenario}{dataset.category}]-{dataset.location}" if dataset else None
            else:
                evaluate_dict['dataset_name'] = None

            items.append(evaluate_dict)

        return {
            'total': pagination.total,  # 总记录数
            'pages': pagination.pages,  # 总页数
            'current_page': pagination.page,  # 当前页码
            'per_page': pagination.per_page,  # 每页数量
            'items': items,  # 当前页的数据
            'search_types': [name.replace('evaluate_', '') for name in search_factory.get_all_strategy_names()
                             if name.startswith('evaluate_')]  # 可用的搜索类型
        }

    @staticmethod
    def get_evaluate_detail(evaluate_uuid):
        """
        获取指定验证任务的详细信息
        :param evaluate_uuid: 验证任务UUID
        :return: 验证任务详细信息
        """
        # 获取验证任务信息
        evaluate = EvaluateInfo.query.get_or_404(evaluate_uuid)
        evaluate_dict = evaluate.to_dict()

        # 获取关联的模型信息
        if evaluate.model_uuid:
            model = ModelInfo.query.get(evaluate.model_uuid)
            evaluate_dict['model_name'] = model.name if model else None
        else:
            evaluate_dict['model_name'] = None

        # 获取关联的数据集信息
        if evaluate.dataset_uuid:
            dataset = DatasetInfo.query.get(evaluate.dataset_uuid)
            evaluate_dict[
                'dataset_name'] = f"[{dataset.scenario}{dataset.category}]-{dataset.location}" if dataset else None
        else:
            evaluate_dict['dataset_name'] = None

        return evaluate_dict

    @staticmethod
    def delete_evaluate(evaluate_uuid):
        """
        删除指定验证任务
        :param evaluate_uuid: 验证任务UUID
        :return: 是否删除成功
        """
        try:
            # 获取验证任务信息
            evaluate = EvaluateInfo.query.get_or_404(evaluate_uuid)

            # 检查并停止可能正在运行的进程
            process_manager = ProcessManager()
            process_status = process_manager.get_process_status(evaluate_uuid)
            if process_status and process_status['status'] == 'running':
                process_manager.stop_process(evaluate_uuid)

            # 删除相关文件
            evaluate.delete_files()

            # 删除数据库记录
            db.session.delete(evaluate)
            db.session.commit()

            return True
        except Exception as e:
            db.session.rollback()
            raise e

    @staticmethod
    def run_evaluate(evaluate_uuid: str) -> Dict:
        """
        运行验证任务
        :param evaluate_uuid: 验证任务UUID
        :return: 运行结果信息
        """
        try:
            # 获取验证任务
            evaluate = EvaluateInfo.query.get_or_404(evaluate_uuid)

            # 检查任务状态
            if evaluate.evaluate_status == EvaluateStatusType.IN_PROGRESS.value:
                raise ValueError("任务正在进行中，无法重复启动")

            # 检查模型
            if not evaluate.model_uuid:
                raise ValueError("未指定关联的模型")
            model = ModelInfo.query.get(evaluate.model_uuid)
            if not model:
                raise ValueError(f"未找到UUID为 {evaluate.model_uuid} 的模型")
            model_detail = ModelDetail.query.filter_by(model_uuid=evaluate.model_uuid).first()
            if not model_detail:
                raise ValueError(f"未找到模型 {model.name} 的详细信息")

            # 检查数据集（如果指定了）
            if evaluate.dataset_uuid:
                dataset = DatasetInfo.query.get(evaluate.dataset_uuid)
                if not dataset:
                    raise ValueError(f"未找到UUID为 {evaluate.dataset_uuid} 的数据集")
                dataset_detail = DatasetDetail.query.filter_by(dataset_uuid=evaluate.dataset_uuid).first()
                if not dataset_detail:
                    raise ValueError(f"未找到数据集 {dataset.category} 的详细信息")

            # 清空输出目录
            output_dir = os.path.join(
                current_app.config['STORAGE_FOLDER'],
                current_app.config['EVALUATE_FOLDER'],
                evaluate.uuid,
                current_app.config['EVALUATE_OUTPUT_FOLDER']
            )
            if os.path.exists(output_dir):
                for item in os.listdir(output_dir):
                    item_path = os.path.join(output_dir, item)
                    if os.path.isfile(item_path):
                        os.unlink(item_path)
                    elif os.path.isdir(item_path):
                        shutil.rmtree(item_path)
            else:
                os.makedirs(output_dir)

            # 构建运行环境
            # 1. 工作目录
            work_dir = os.path.dirname(os.path.join(
                current_app.config['STORAGE_FOLDER'],
                model_detail.code_file_path
            ))
            print(work_dir)

            # 2. 环境变量
            env = os.environ.copy()
            env_path = os.path.join(
                current_app.config['STORAGE_FOLDER'],
                model_detail.env_file_path,
                'Library',
                'bin'
            )
            env["PATH"] = env_path + os.pathsep + env["PATH"]

            # 3. Python解释器路径
            python_exe = os.path.join(
                current_app.config['STORAGE_FOLDER'],
                model_detail.env_file_path,
                'python.exe'
            )

            # 4. 脚本路径
            script_path = os.path.join(
                current_app.config['STORAGE_FOLDER'],
                model_detail.code_file_path
            )

            # 5. 输入目录
            input_dir = ""
            if evaluate.dataset_uuid and evaluate.evaluate_type != 4:
                input_dir = os.path.join(
                    current_app.config['STORAGE_FOLDER'],
                    current_app.config['DATASET_FOLDER'],
                    dataset_detail.input_path
                )
                # 确保输入目录存在
                if not os.path.exists(input_dir):
                    raise ValueError(f"输入目录不存在: {input_dir}")

            # 5. 输出目录
            output_dir = os.path.join(
                current_app.config['STORAGE_FOLDER'],
                current_app.config['EVALUATE_FOLDER'],
                evaluate.uuid,
                current_app.config['EVALUATE_OUTPUT_FOLDER']
            )

            # 构建命令
            cmd = [python_exe, script_path]

            # main.py 期望的参数顺序：input_path output_path
            if input_dir:
                cmd.append(input_dir)
            cmd.append(output_dir)

            # 额外参数放在最后
            if evaluate.extra_parameter:
                # 如果额外参数包含空格，需要正确分割
                extra_params = evaluate.extra_parameter.strip()
                if extra_params:
                    # 简单的参数分割，支持引号包围的参数
                    import shlex
                    try:
                        cmd.extend(shlex.split(extra_params))
                    except ValueError:
                        # 如果分割失败，直接添加
                        cmd.append(extra_params)

            # 更新任务状态
            evaluate.evaluate_status = EvaluateStatusType.IN_PROGRESS.value
            db.session.commit()

            # 记录详细的启动信息
            current_app.logger.info(f"启动验证任务 {evaluate.uuid}")
            current_app.logger.info(f"Python解释器: {python_exe}")
            current_app.logger.info(f"脚本路径: {script_path}")
            current_app.logger.info(f"工作目录: {work_dir}")
            current_app.logger.info(f"输入目录: {input_dir}")
            current_app.logger.info(f"输出目录: {output_dir}")
            current_app.logger.info(f"完整命令: {' '.join(cmd)}")

            # 启动进程
            process_manager = ProcessManager()
            if process_manager.start_process(evaluate.uuid, cmd, work_dir, env, EvaluateService._on_process_complete):
                return {
                    'process_id': evaluate.uuid,
                    'message': '验证任务已启动',
                    'running_count': process_manager.get_running_process_count(),
                    'max_processes': process_manager.get_max_processes(),
                    'command': ' '.join(cmd),
                    'work_dir': work_dir,
                    'python_exe': python_exe
                }
            else:
                # 如果启动失败，恢复任务状态
                evaluate.evaluate_status = EvaluateStatusType.NOT_STARTED.value
                db.session.commit()
                raise RuntimeError("启动验证任务失败")

        except Exception as e:
            # 如果发生错误，恢复任务状态
            if 'evaluate' in locals():
                evaluate.evaluate_status = EvaluateStatusType.NOT_STARTED.value
                db.session.commit()
            raise e
