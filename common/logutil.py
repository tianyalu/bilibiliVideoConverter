import logging
import os


# 初始化 logger 的方法
def init_logger(log_path='', log_name='err_log'):
    # 创建日志记录器
    logger= logging.getLogger(log_name)
    logger.setLevel(logging.ERROR)

    # 创建文件处理器
    name = f'{log_name}.log' if log_path else os.path.join(log_path, f'{log_name}.log')
    # print(f'log name: {name}')
    file_handler = logging.FileHandler(name, mode='a', encoding='utf-8')  # 使用日志名称作为文件名
    file_handler.setLevel(logging.ERROR)

    # 配置日志格式
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)

    # 将文件处理器添加到日志记录器中
    logger.addHandler(file_handler)
    return logger

