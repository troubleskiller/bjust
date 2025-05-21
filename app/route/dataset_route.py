"""
数据集相关API路由
"""
import os
import tempfile
from http import HTTPStatus
from flask import Blueprint, request, current_app, jsonify
from werkzeug.utils import secure_filename
from app.service.dataset_upload_service import DatasetUploadService
from app.service.dataset_service import DatasetService
from app.utils.response import ServerResponse

bp = Blueprint('dataset', __name__)

@bp.route('/upload', methods=['POST'])
def upload_dataset():
    """
    处理数据集上传
    请求体应为multipart/form-data格式，包含一个名为'dataset_package'的文件字段
    """
    if 'dataset_package' not in request.files:
        return jsonify(
            ServerResponse.error("未找到上传文件", HTTPStatus.BAD_REQUEST.value).model_dump()
        ), HTTPStatus.BAD_REQUEST.value
        
    file = request.files['dataset_package']
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
        
        # 处理数据集上传
        dataset_uuid = DatasetUploadService.process_dataset_upload(temp_file, os.path.join(temp_dir, 'extract'))
        
        return jsonify(
            ServerResponse.success(
                data={'dataset_uuid': dataset_uuid},
                message='数据集上传成功'
            ).model_dump()
        ), HTTPStatus.OK.value
        
    except Exception as e:
        return jsonify(
            ServerResponse.error(f"数据集上传失败：{str(e)}", HTTPStatus.INTERNAL_SERVER_ERROR.value).model_dump()
        ), HTTPStatus.INTERNAL_SERVER_ERROR.value

@bp.route('/list', methods=['GET'])
def get_dataset_list():
    """
    获取数据集列表（分页）
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
        
        result = DatasetService.get_dataset_list(
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
            ServerResponse.error(f"获取数据集列表失败：{str(e)}", HTTPStatus.INTERNAL_SERVER_ERROR.value).model_dump()
        ), HTTPStatus.INTERNAL_SERVER_ERROR.value

@bp.route('/<dataset_uuid>', methods=['GET'])
def get_dataset_detail(dataset_uuid):
    """
    获取指定数据集的详细信息
    :param dataset_uuid: 数据集UUID
    """
    try:
        result = DatasetService.get_dataset_detail(dataset_uuid)
        
        return jsonify(
            ServerResponse.success(
                data=result,
                message='获取成功'
            ).model_dump()
        ), HTTPStatus.OK.value
        
    except Exception as e:
        return jsonify(
            ServerResponse.error(f"获取数据集详情失败：{str(e)}", HTTPStatus.INTERNAL_SERVER_ERROR.value).model_dump()
        ), HTTPStatus.INTERNAL_SERVER_ERROR.value

@bp.route('/<dataset_uuid>', methods=['DELETE'])
def delete_dataset(dataset_uuid):
    """
    删除指定数据集
    :param dataset_uuid: 数据集UUID
    """
    try:
        DatasetService.delete_dataset(dataset_uuid)
        
        return jsonify(
            ServerResponse.success(
                message='删除成功'
            ).model_dump()
        ), HTTPStatus.OK.value
        
    except Exception as e:
        return jsonify(
            ServerResponse.error(f"删除数据集失败：{str(e)}", HTTPStatus.INTERNAL_SERVER_ERROR.value).model_dump()
        ), HTTPStatus.INTERNAL_SERVER_ERROR.value
