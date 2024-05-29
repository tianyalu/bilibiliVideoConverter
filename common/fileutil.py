import os


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