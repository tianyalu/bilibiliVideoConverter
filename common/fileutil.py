from datetime import datetime
import os
import random


# 目录不存在时创建目录
def create_directory(directory_path):
    try:
        if not os.path.exists(directory_path):
            os.makedirs(directory_path)
            print(f"目录'{directory_path}'已创建")
        # else:
            # print(f"目录'{directory_path}'已存在")
    except Exception as e:
        print(f"创建目录时发生错误：{e}")


# 根据原文件名返回带时间戳后缀+随机数的文件名以避免重名
def get_random_file_name(ori_file_name):
    name_without_extension = ori_file_name.rsplit('.', 1)[0]  # 从右边开始分割，最多分割一次
    extension = ori_file_name.split('.')[-1]
    cur_time = datetime.now()
    time_str = cur_time.strftime("%m%d%H%M%S")  # 添加时间戳避免重名覆盖
    random_str = random.randint(10, 99)
    new_file_name = f'{name_without_extension}_{time_str}_{random_str}.{extension}'
    return new_file_name
