import re


# 过滤Windows文件名中的非法字符
def file_name_filter(file_name):
    invalid_chars = r'[\\\/:*?"<>|]|\uFF1F'  # \uFF1F 是全角问号的 Unicode
    replace_char = ''
    filename = re.sub(invalid_chars, replace_char, file_name)
    filename = filename.replace(' ', '')
    return filename


if __name__ == "__main__":
    str = '[写真]我怀揣着罪恶? 等待着救赎? 摄影-第1张'
    name = file_name_filter(str)
    print(name)
