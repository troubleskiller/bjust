from . import db
from sqlalchemy import String, Column, DateTime, Text, Integer, Date
from datetime import datetime

class BestPracticeCase(db.Model):
    __tablename__ = 'best_practice_cases'

    id = Column(Integer, primary_key=True, autoincrement=True)
    case_dir_name = Column(String(255), unique=True, nullable=False)
    case_img_path = Column(String(512), nullable=False) # 存储图片路径
    case_type = Column(String(50), nullable=False) # 例如: "real_data", "simulation", "no_label"
    case_title = Column(String(255), nullable=False)
    model_name = Column(Text, nullable=True) # 逗号分隔的模型名称字符串
    model_type_name = Column(Text, nullable=True) # 逗号分隔的模型类型名称字符串
    create_date_str = Column(String(20), nullable=True) # API中为 "YYYY-MM-DD" 格式字符串
    # 或者使用 Date 类型: create_date = Column(Date, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow) 