"""
数据集服务层
"""
from app import db
from app.model.dataset_info import DatasetInfo
from app.model.dataset_detail import DatasetDetail
from app.model.evaluate_info import EvaluateInfo, EvaluateStatusType
from app.service.search.search_factory import search_factory

class DatasetService:
    """数据集服务类"""
    
    @staticmethod
    def check_dataset_in_use(dataset_uuid):
        """
        检查数据集是否正在被验证任务使用
        :param dataset_uuid: 数据集UUID
        :return: (bool, str) - (是否在使用中, 错误信息)
        """
        # 查询是否有进行中的验证任务使用了该数据集
        in_use = EvaluateInfo.query.filter_by(
            dataset_uuid=dataset_uuid,
            evaluate_status=EvaluateStatusType.IN_PROGRESS.value
        ).first() is not None
        
        if in_use:
            return True, "该数据集正在被验证任务使用，无法删除"
        return False, ""

    @staticmethod
    def get_dataset_list(page=1, per_page=10, search_type=None, search_term=None):
        """
        分页获取数据集列表
        :param page: 页码（从1开始）
        :param per_page: 每页数量
        :param search_type: 搜索类型
        :param search_term: 搜索关键词
        :return: 数据集列表和分页信息
        """
        # 创建基础查询
        query = DatasetInfo.query
        
        # 如果指定了搜索类型和关键词，应用搜索策略
        if search_type and search_term:
            try:
                # 添加数据集前缀
                strategy = search_factory.get_strategy(f"dataset_{search_type}")
                query = strategy.apply(query, search_term)
            except ValueError as e:
                raise ValueError(f"搜索类型无效：{str(e)}")
        
        # 应用排序
        query = query.order_by(DatasetInfo.updated_at.desc())
        
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
            'search_types': [name.replace('dataset_', '') for name in search_factory.get_all_strategy_names() 
                           if name.startswith('dataset_')]  # 可用的搜索类型
        }
    
    @staticmethod
    def get_dataset_detail(dataset_uuid):
        """
        获取指定数据集的详细信息
        :param dataset_uuid: 数据集UUID
        :return: 数据集详细信息（包括基础信息和详情信息）
        """
        # 获取数据集基础信息
        dataset = DatasetInfo.query.get_or_404(dataset_uuid)
        dataset_dict = dataset.to_dict()
        
        # 获取数据集详情
        if dataset.detail:
            dataset_dict['detail'] = dataset.detail.to_dict()
        else:
            dataset_dict['detail'] = None
            
        return dataset_dict
    
    @staticmethod
    def delete_dataset(dataset_uuid):
        """
        删除指定数据集
        :param dataset_uuid: 数据集UUID
        :return: 是否删除成功
        :raises: ValueError 如果数据集正在使用中
        """
        # 检查数据集是否在使用中
        in_use, error_msg = DatasetService.check_dataset_in_use(dataset_uuid)
        if in_use:
            raise ValueError(error_msg)
            
        try:
            # 获取数据集信息
            dataset = DatasetInfo.query.get_or_404(dataset_uuid)
            
            # 如果存在详情，先删除相关文件
            if dataset.detail:
                dataset.detail.delete_files()
            
            # 删除数据库记录（级联删除会自动删除详情记录）
            db.session.delete(dataset)
            db.session.commit()
            
            return True
        except Exception as e:
            db.session.rollback()
            raise e 