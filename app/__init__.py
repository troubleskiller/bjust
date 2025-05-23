"""
Flask应用初始化
"""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from config import Config

# 初始化数据库
db = SQLAlchemy()
# 初始化迁移器
migrate = Migrate()

from app.route.homepage_route import homepage_bp
from app.route.online_deduction_route import online_deduction_bp
from app.route.model_plaza_route import model_plaza_bp
from app.route.channel_dataset_route import channel_dataset_bp
from app.route.model_validation_route import model_validation_bp
from app.route.dataset_route import dataset_bp
from app.route.model_route import model_bp

def create_app():
    """
    创建Flask应用实例
    :return: Flask应用实例
    """
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # 初始化CORS
    CORS(app)
    
    # 初始化扩展
    db.init_app(app)
    Migrate(app=app, db=db)
    
    # 注册蓝图
    from app.route import model_route, storage_route, dataset_route, dev_route, evaluate_route
    app.register_blueprint(storage_route.bp)
    app.register_blueprint(dev_route.bp, url_prefix='/dev')
    app.register_blueprint(evaluate_route.bp, url_prefix='/api/evaluate')
    app.register_blueprint(homepage_bp)
    app.register_blueprint(dataset_bp)
    app.register_blueprint(model_bp,url_prefix='/api/model')
    app.register_blueprint(online_deduction_bp)
    app.register_blueprint(model_plaza_bp)
    app.register_blueprint(channel_dataset_bp)
    app.register_blueprint(model_validation_bp)
    
    # 创建数据库表
    # with app.app_context():
    #     db.create_all()
    
    return app 