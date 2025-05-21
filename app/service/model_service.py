"""
模型服务层
"""
from app import db
from app.model.model_info import ModelInfo
from app.model.model_detail import ModelDetail
from app.model.evaluate_info import EvaluateInfo, EvaluateStatusType
from app.service.search.search_factory import search_factory

class ModelService:
    """模型服务类"""
    
    @staticmethod
    def get_model_list(page=1, per_page=10, search_type=None, search_term=None):
        """
        分页获取模型列表
        :param page: 页码（从1开始）
        :param per_page: 每页数量
        :param search_type: 搜索类型
        :param search_term: 搜索关键词
        :return: 模型列表和分页信息
        """
        # 创建基础查询
        query = ModelInfo.query
        
        # 如果指定了搜索类型和关键词，应用搜索策略
        if search_type and search_term:
            try:
                # 添加模型前缀
                strategy = search_factory.get_strategy(f"model_{search_type}")
                query = strategy.apply(query, search_term)
            except ValueError as e:
                raise ValueError(f"搜索类型无效：{str(e)}")
        
        # 应用排序
        query = query.order_by(ModelInfo.updated_at.desc())
        
        # 执行分页查询
        pagination = query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
        
        return {
            'total': pagination.total,  # 总记录数
            'pages': pagination.pages,  # 总页数
            'current_page': pagination.page,  # 当前页码
            'per_page': pagination.per_page,  # 每页数量
            'items': [item.to_dict() for item in pagination.items],  # 当前页的数据
            'search_types': [name.replace('model_', '') for name in search_factory.get_all_strategy_names() 
                           if name.startswith('model_')]  # 可用的搜索类型
        }
    
    @staticmethod
    def get_model_detail(model_uuid):
        """
        获取指定模型的详细信息
        :param model_uuid: 模型UUID
        :return: 模型详细信息（包括基础信息和详情信息）
        """
        # 获取模型基础信息
        model = ModelInfo.query.get_or_404(model_uuid)
        model_dict = model.to_dict()
        
        # 获取模型详情
        if model.detail:
            model_dict['detail'] = model.detail.to_dict()
        else:
            model_dict['detail'] = None
            
        return model_dict
    
    @staticmethod
    def check_model_in_use(model_uuid):
        """
        检查模型是否正在被验证任务使用
        :param model_uuid: 模型UUID
        :return: (bool, str) - (是否在使用中, 错误信息)
        """
        # 查询是否有进行中的验证任务使用了该模型
        in_use = EvaluateInfo.query.filter_by(
            model_uuid=model_uuid,
            evaluate_status=EvaluateStatusType.IN_PROGRESS.value
        ).first() is not None
        
        if in_use:
            return True, "该模型正在被验证任务使用，无法删除"
        return False, ""

    @staticmethod
    def delete_model(model_uuid):
        """
        删除指定模型
        :param model_uuid: 模型UUID
        :return: 是否删除成功
        :raises: ValueError 如果模型正在使用中
        """
        # 检查模型是否在使用中
        in_use, error_msg = ModelService.check_model_in_use(model_uuid)
        if in_use:
            raise ValueError(error_msg)
            
        try:
            # 获取模型信息
            model = ModelInfo.query.get_or_404(model_uuid)
            
            # 如果存在详情，先删除相关文件
            if model.detail:
                model.detail.delete_files()
            
            # 删除数据库记录（级联删除会自动删除详情记录）
            db.session.delete(model)
            db.session.commit()
            
            return True
        except Exception as e:
            db.session.rollback()
            raise e 