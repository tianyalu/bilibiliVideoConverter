import re


# 过滤Windows文件名中的非法字符
def file_name_filter(file_name):
    invalid_chars = '[\\\/:*?？"<>|]'
    replace_char = ''
    filename = re.sub(invalid_chars, replace_char, file_name)
    return filename
