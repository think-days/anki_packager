import logging
import os
from logging.handlers import RotatingFileHandler
import time

# ANSI escape codes for bold blue
BOLD_BLUE = "\033[1;34m"
RESET = "\033[0m"

def setup_logger():
    """设置日志配置，包含自动清理功能"""
    # 创建日志目录
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    log_file = os.path.join(log_dir, "anki_packager.log")
    
    # 设置日志格式
    formatter = logging.Formatter(
        f"{BOLD_BLUE}[%(filename)s:%(lineno)d:%(funcName)s]{RESET} %(message)s"
    )
    
    # 使用RotatingFileHandler实现日志轮转
    # maxBytes: 单个日志文件最大10MB
    # backupCount: 保留5个备份文件
    file_handler = RotatingFileHandler(
        log_file, 
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setFormatter(formatter)
    
    # 控制台输出
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    
    # 配置根日志器
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
    
    # 设置第三方库的日志级别
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("openai").setLevel(logging.WARNING)
    
    return logging.getLogger(__name__)

# 初始化日志器
logger = setup_logger()

def cleanup_old_logs():
    """清理超过30天的旧日志文件"""
    log_dir = "logs"
    if not os.path.exists(log_dir):
        return
    
    current_time = time.time()
    max_age = 30 * 24 * 60 * 60  # 30天
    
    for filename in os.listdir(log_dir):
        if filename.endswith('.log'):
            file_path = os.path.join(log_dir, filename)
            file_age = current_time - os.path.getmtime(file_path)
            
            if file_age > max_age:
                try:
                    os.remove(file_path)
                    logger.info(f"已删除旧日志文件: {filename}")
                except Exception as e:
                    logger.warning(f"删除日志文件失败 {filename}: {e}")

# 启动时清理旧日志
cleanup_old_logs()
