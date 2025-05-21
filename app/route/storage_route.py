"""
静态文件访问路由
"""
import os
from flask import Blueprint, send_from_directory, current_app, abort
from http import HTTPStatus

bp = Blueprint('static', __name__)

@bp.route('/storage/<path:filename>')
def serve_storage(filename):
    """
    提供存储文件的访问服务
    :param filename: 文件路径（相对于STORAGE_FOLDER的路径）
    """
    try:
        # 获取存储根目录
        storage_path = current_app.config['STORAGE_FOLDER']
        
        # 检查请求的文件是否在允许的目录中
        if not (filename.startswith('model/') or filename.startswith('dataset/') or filename.startswith('evaluate/')):
            abort(403)  # 禁止访问非模型文件目录
            
        # 获取文件所在目录和文件名
        directory = os.path.dirname(os.path.join(storage_path, filename))
        file_name = os.path.basename(filename)
        
        return send_from_directory(directory, file_name)
    except Exception as e:
        current_app.logger.error(f"访问文件失败：{str(e)}")
        abort(404)  # 文件不存在或无法访问 