"""
数据库迁移管理脚本
"""
from flask.cli import FlaskGroup
from app import create_app, db

cli = FlaskGroup(create_app=create_app)

if __name__ == '__main__':
    cli() 