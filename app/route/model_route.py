"""
模型相关API路由
"""
import os
import tempfile
from http import HTTPStatus
from flask import Blueprint, request, current_app, jsonify
from werkzeug.utils import secure_filename
from app.service.model_upload_service import ModelUploadService
from app.service.model_service import ModelService
from app.utils.response import ServerResponse

bp = Blueprint('model', __name__)

@bp.route('/upload', methods=['POST'])
def upload_model():
    """
    处理模型上传
    请求体应为multipart/form-data格式，包含一个名为'model_package'的文件字段
    """
    if 'model_package' not in request.files:
        return jsonify(
            ServerResponse.error("未找到上传文件", HTTPStatus.BAD_REQUEST.value).model_dump()
        ), HTTPStatus.BAD_REQUEST.value
        
    file = request.files['model_package']
    if not file.filename:
        return jsonify(
            ServerResponse.error("文件名不能为空", HTTPStatus.BAD_REQUEST.value).model_dump()
        ), HTTPStatus.BAD_REQUEST.value
        
    # 创建临时目录
    temp_dir = tempfile.mkdtemp()
    temp_file = os.path.join(temp_dir, secure_filename(file.filename))
    
    try:
        # 保存上传的文件
        file.save(temp_file)
        
        # 处理模型上传
        model_uuid = ModelUploadService.process_model_upload(temp_file, os.path.join(temp_dir, 'extract'))
        
        return jsonify(
            ServerResponse.success(
                data={'model_uuid': model_uuid},
                message='模型上传成功'
            ).model_dump()
        ), HTTPStatus.OK.value
        
    except Exception as e:
        return jsonify(
            ServerResponse.error(f"模型上传失败：{str(e)}", HTTPStatus.INTERNAL_SERVER_ERROR.value).model_dump()
        ), HTTPStatus.INTERNAL_SERVER_ERROR.value

@bp.route('/list', methods=['GET'])
def get_model_list():
    """
    获取模型列表（分页）
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
        
        result = ModelService.get_model_list(
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
            ServerResponse.error(f"获取模型列表失败：{str(e)}", HTTPStatus.INTERNAL_SERVER_ERROR.value).model_dump()
        ), HTTPStatus.INTERNAL_SERVER_ERROR.value

@bp.route('/<model_uuid>', methods=['GET'])
def get_model_detail(model_uuid):
    """
    获取指定模型的详细信息
    :param model_uuid: 模型UUID
    """
    try:
        result = ModelService.get_model_detail(model_uuid)
        
        return jsonify(
            ServerResponse.success(
                data=result,
                message='获取成功'
            ).model_dump()
        ), HTTPStatus.OK.value
        
    except Exception as e:
        return jsonify(
            ServerResponse.error(f"获取模型详情失败：{str(e)}", HTTPStatus.INTERNAL_SERVER_ERROR.value).model_dump()
        ), HTTPStatus.INTERNAL_SERVER_ERROR.value

@bp.route('/<model_uuid>', methods=['DELETE'])
def delete_model(model_uuid):
    """
    删除指定模型
    :param model_uuid: 模型UUID
    """
    try:
        ModelService.delete_model(model_uuid)
        
        return jsonify(
            ServerResponse.success(
                message='删除成功'
            ).model_dump()
        ), HTTPStatus.OK.value
        
    except Exception as e:
        return jsonify(
            ServerResponse.error(f"删除模型失败：{str(e)}", HTTPStatus.INTERNAL_SERVER_ERROR.value).model_dump()
        ), HTTPStatus.INTERNAL_SERVER_ERROR.value
