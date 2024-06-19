# 该项目的作用是将B站缓存的视频（video.m4s,audio.m4s）批量转换为MP4格式

from bilibiliConverter import bilibiliConverter


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print('PyCharm')
    bilibiliConverter.convert_normal_video()

