"""
安全文件解压工具类
"""
import os
import zipfile
import concurrent.futures
import threading
import pathlib
from app.utils.logger import setup_logger

class SafeExtractor:
    """
    安全的文件解压器，支持多线程并发解压
    """
    def __init__(self, zip_path: str, dest_path: str):
        """
        初始化解压器
        @param zip_path: zip文件路径
        @param dest_path: 解压目标路径
        """
        self.zip_path = zip_path
        self.dest_path = dest_path
        self.file_locks = {}  # 文件锁字典
        self.lock = threading.Lock()  # 全局锁
        self.logger = setup_logger('safe_extractor')  # 创建日志记录器
        self._ensure_dest_dir()

    def _ensure_dest_dir(self):
        """
        确保目标目录存在
        """
        try:
            pathlib.Path(self.dest_path).mkdir(parents=True, exist_ok=True)
        except Exception as e:
            self.logger.error(f"创建目标目录失败: {e}")
            raise

    def _get_file_lock(self, file_path: str) -> threading.Lock:
        """
        获取文件锁
        @param file_path: 文件路径
        @return: 文件锁
        """
        with self.lock:
            if file_path not in self.file_locks:
                self.file_locks[file_path] = threading.Lock()
            return self.file_locks[file_path]

    def _safe_extract_file(self, zf: zipfile.ZipFile, member: zipfile.ZipInfo) -> bool:
        """
        安全地解压单个文件
        @param zf: zip文件对象
        @param member: zip成员信息
        @return: 是否解压成功
        """
        target_path = os.path.join(self.dest_path, member.filename)
        
        # 如果是目录，直接创建
        if member.filename.endswith('/'):
            try:
                pathlib.Path(target_path).mkdir(parents=True, exist_ok=True)
                return True
            except Exception as e:
                self.logger.error(f"创建目录失败 {member.filename}: {e}")
                return False

        # 获取文件锁
        file_lock = self._get_file_lock(target_path)
        
        try:
            with file_lock:
                # 如果文件已存在，跳过
                if os.path.exists(target_path):
                    self.logger.debug(f"文件已存在，跳过: {member.filename}")
                    return True
                
                # 确保目标文件的父目录存在
                pathlib.Path(os.path.dirname(target_path)).mkdir(parents=True, exist_ok=True)
                
                # 解压文件
                try:
                    zf.extract(member, self.dest_path)
                    return True
                except Exception as e:
                    self.logger.error(f"解压文件失败 {member.filename}: {e}")
                    return False
        except Exception as e:
            self.logger.error(f"处理文件失败 {member.filename}: {e}")
            return False

    def extract_all(self) -> bool:
        """
        解压所有文件
        @return: 是否全部解压成功
        """
        try:
            with open(self.zip_path, 'rb') as f:
                zf = zipfile.ZipFile(f)
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    futures = [
                        executor.submit(self._safe_extract_file, zf, member)
                        for member in zf.infolist()
                    ]
                    results = [future.result() for future in concurrent.futures.as_completed(futures)]
                    success = all(results)
                    if success:
                        self.logger.info(f"文件解压完成: {self.zip_path}")
                    else:
                        self.logger.error(f"文件解压部分失败: {self.zip_path}")
                    return success
        except Exception as e:
            self.logger.error(f"解压过程发生错误: {e}")
            return False 