"""
应用入口点
"""
from app import create_app

app = create_app()

if __name__ == '__main__':
    app.run() 