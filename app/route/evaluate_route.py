"""
验证任务相关API路由
"""
from http import HTTPStatus
from flask import Blueprint, request, jsonify
from app.service.evaluate_service import EvaluateService
from app.service.evaluate_result_service import EvaluateResultService
from app.utils.response import ServerResponse

# 创建蓝图
bp = Blueprint('evaluate', __name__)

@bp.route('/create', methods=['POST'])
def create_evaluate():
    """
    创建新的验证任务
    请求体参数：
    - evaluate_type: 验证任务类型(1-4)
    - model_uuid: 关联的模型UUID（可选）
    - dataset_uuid: 关联的数据集UUID（可选）
    - extra_parameter: 额外参数（可选）
    """
    try:
        data = request.get_json()
        evaluate_type = data.get('evaluate_type', 1)
        model_uuid = data.get('model_uuid')
        dataset_uuid = data.get('dataset_uuid')
        extra_parameter = data.get('extra_parameter')
        
        result = EvaluateService.create_evaluate(
            evaluate_type=evaluate_type,
            model_uuid=model_uuid,
            dataset_uuid=dataset_uuid,
            extra_parameter=extra_parameter
        )
        
        return jsonify(
            ServerResponse.success(
                data=result,
                message='创建成功'
            ).model_dump()
        ), HTTPStatus.OK.value
        
    except ValueError as e:
        return jsonify(
            ServerResponse.error(str(e), HTTPStatus.BAD_REQUEST.value).model_dump()
        ), HTTPStatus.BAD_REQUEST.value
    except Exception as e:
        return jsonify(
            ServerResponse.error(f"创建验证任务失败：{str(e)}", HTTPStatus.INTERNAL_SERVER_ERROR.value).model_dump()
        ), HTTPStatus.INTERNAL_SERVER_ERROR.value

@bp.route('/list', methods=['GET'])
def get_evaluate_list():
    """
    获取验证任务列表（分页）
    查询参数：
    - page: 页码（默认1）
    - per_page: 每页数量（默认10）
    - search_type: 搜索类型（可选）
    - search_term: 搜索关键词（可选）
    """
    try:
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))
        search_type = request.args.get('search_type')
        search_term = request.args.get('search_term')
        
        result = EvaluateService.get_evaluate_list(
            page=page,
            per_page=per_page,
            search_type=search_type,
            search_term=search_term
        )
        
        return jsonify(
            ServerResponse.success(
                data=result,
                message='获取成功'
            ).model_dump()
        ), HTTPStatus.OK.value
        
    except ValueError as e:
        return jsonify(
            ServerResponse.error(str(e), HTTPStatus.BAD_REQUEST.value).model_dump()
        ), HTTPStatus.BAD_REQUEST.value
    except Exception as e:
        return jsonify(
            ServerResponse.error(f"获取验证任务列表失败：{str(e)}", HTTPStatus.INTERNAL_SERVER_ERROR.value).model_dump()
        ), HTTPStatus.INTERNAL_SERVER_ERROR.value

@bp.route('/<evaluate_uuid>', methods=['GET'])
def get_evaluate_detail(evaluate_uuid):
    """
    获取指定验证任务的详细信息
    :param evaluate_uuid: 验证任务UUID
    """
    try:
        result = EvaluateService.get_evaluate_detail(evaluate_uuid)
        
        return jsonify(
            ServerResponse.success(
                data=result,
                message='获取成功'
            ).model_dump()
        ), HTTPStatus.OK.value
        
    except Exception as e:
        return jsonify(
            ServerResponse.error(f"获取验证任务详情失败：{str(e)}", HTTPStatus.INTERNAL_SERVER_ERROR.value).model_dump()
        ), HTTPStatus.INTERNAL_SERVER_ERROR.value

@bp.route('/<evaluate_uuid>/update', methods=['POST'])
def update_evaluate(evaluate_uuid):
    """
    更新验证任务信息
    :param evaluate_uuid: 验证任务UUID
    请求体参数：
    - evaluate_type: 验证任务类型(1-4)（可选）
    - model_uuid: 关联的模型UUID（可选）
    - dataset_uuid: 关联的数据集UUID（可选）
    - extra_parameter: 额外参数（可选）
    """
    try:
        data = request.get_json()
        evaluate_type = int(data.get('evaluate_type'))
        model_uuid = data.get('model_uuid')
        dataset_uuid = data.get('dataset_uuid')
        extra_parameter = data.get('extra_parameter')
        result = EvaluateService.update_evaluate(
            evaluate_uuid=evaluate_uuid,
            evaluate_type=evaluate_type,
            model_uuid=model_uuid,
            dataset_uuid=dataset_uuid,
            extra_parameter=extra_parameter
        )
        
        return jsonify(
            ServerResponse.success(
                data=result,
                message='更新成功'
            ).model_dump()
        ), HTTPStatus.OK.value
        
    except ValueError as e:
        return jsonify(
            ServerResponse.error(str(e), HTTPStatus.BAD_REQUEST.value).model_dump()
        ), HTTPStatus.BAD_REQUEST.value
    except Exception as e:
        return jsonify(
            ServerResponse.error(f"更新验证任务失败：{str(e)}", HTTPStatus.INTERNAL_SERVER_ERROR.value).model_dump()
        ), HTTPStatus.INTERNAL_SERVER_ERROR.value

@bp.route('/<evaluate_uuid>', methods=['DELETE'])
def delete_evaluate(evaluate_uuid):
    """
    删除指定验证任务
    :param evaluate_uuid: 验证任务UUID
    """
    try:
        EvaluateService.delete_evaluate(evaluate_uuid)
        
        return jsonify(
            ServerResponse.success(
                message='删除成功'
            ).model_dump()
        ), HTTPStatus.OK.value
        
    except Exception as e:
        return jsonify(
            ServerResponse.error(f"删除验证任务失败：{str(e)}", HTTPStatus.INTERNAL_SERVER_ERROR.value).model_dump()
        ), HTTPStatus.INTERNAL_SERVER_ERROR.value

@bp.route('/<evaluate_uuid>/run', methods=['POST'])
def run_evaluate(evaluate_uuid):
    """
    运行验证任务
    :param evaluate_uuid: 验证任务UUID
    """
    try:
        result = EvaluateService.run_evaluate(evaluate_uuid)
        
        return jsonify(
            ServerResponse.success(
                data=result,
                message='任务启动成功'
            ).model_dump()
        ), HTTPStatus.OK.value
        
    except ValueError as e:
        return jsonify(
            ServerResponse.error(str(e), HTTPStatus.BAD_REQUEST.value).model_dump()
        ), HTTPStatus.BAD_REQUEST.value
    except Exception as e:
        return jsonify(
            ServerResponse.error(f"启动验证任务失败：{str(e)}", HTTPStatus.INTERNAL_SERVER_ERROR.value).model_dump()
        ), HTTPStatus.INTERNAL_SERVER_ERROR.value

@bp.route('/<evaluate_uuid>/status', methods=['GET'])
def get_evaluate_status(evaluate_uuid):
    """
    获取验证任务进程状态
    :param evaluate_uuid: 验证任务UUID
    """
    try:
        result = EvaluateService.get_process_status(evaluate_uuid)
        
        return jsonify(
            ServerResponse.success(
                data=result,
                message='获取成功'
            ).model_dump()
        ), HTTPStatus.OK.value
        
    except Exception as e:
        return jsonify(
            ServerResponse.error(f"获取验证任务状态失败：{str(e)}", HTTPStatus.INTERNAL_SERVER_ERROR.value).model_dump()
        ), HTTPStatus.INTERNAL_SERVER_ERROR.value

@bp.route('/<evaluate_uuid>/stop', methods=['POST'])
def stop_evaluate(evaluate_uuid):
    """
    停止验证任务进程
    :param evaluate_uuid: 验证任务UUID
    """
    try:
        if EvaluateService.stop_process(evaluate_uuid):
            return jsonify(
                ServerResponse.success(
                    message='停止成功'
                ).model_dump()
            ), HTTPStatus.OK.value
        else:
            return jsonify(
                ServerResponse.error(
                    "停止验证任务失败",
                    HTTPStatus.INTERNAL_SERVER_ERROR.value
                ).model_dump()
            ), HTTPStatus.INTERNAL_SERVER_ERROR.value
            
    except ValueError as e:
        return jsonify(
            ServerResponse.error(str(e), HTTPStatus.BAD_REQUEST.value).model_dump()
        ), HTTPStatus.BAD_REQUEST.value
    except Exception as e:
        return jsonify(
            ServerResponse.error(f"停止验证任务失败：{str(e)}", HTTPStatus.INTERNAL_SERVER_ERROR.value).model_dump()
        ), HTTPStatus.INTERNAL_SERVER_ERROR.value

@bp.route('/<evaluate_uuid>/result', methods=['GET'])
def get_evaluate_result(evaluate_uuid):
    """
    获取验证任务的最新结果
    :param evaluate_uuid: 验证任务UUID
    查询参数：
    - index: 可选参数，指定要获取数据的序号（从0开始）
    """
    try:
        # 获取可选的index参数
        index = request.args.get('index')
        # 如果提供了index参数，将其转换为整数
        if index is not None:
            try:
                index = int(index)
            except ValueError:
                return jsonify(
                    ServerResponse.error("index参数必须是整数", HTTPStatus.BAD_REQUEST.value).model_dump()
                ), HTTPStatus.BAD_REQUEST.value
        
        result = EvaluateResultService.get_evaluate_latest_result(evaluate_uuid, index)
        
        return jsonify(
            ServerResponse.success(
                data=result,
                message='获取成功'
            ).model_dump()
        ), HTTPStatus.OK.value
        
    except Exception as e:
        return jsonify(
            ServerResponse.error(f"获取验证任务结果失败：{str(e)}", HTTPStatus.INTERNAL_SERVER_ERROR.value).model_dump()
        ), HTTPStatus.INTERNAL_SERVER_ERROR.value 