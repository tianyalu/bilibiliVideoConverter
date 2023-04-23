# 该项目的作用是将B站缓存的视频（video.m4s,audio.m4s）批量转换为MP4格式
# 参考：https://www.bilibili.com/read/cv18052742/

import os
import subprocess
import shutil
import json
import re

myDir = 'F:/bilibiliVideoDLSmall/test'  # 存放从手机复制而来的文件夹的地方
# myDir = 'F:/Video/down/AfunDownload/Nox_share/ImageShare/BibiliDownload/test'  # 存放从手机复制而来的文件夹的地方
finalDir = 'F:/bilibiliVideoDLOutput'  # 存放最终MP4文件的地方
# finalDir = 'F:/Video/down/BilibiliDownload2/di7'  # 存放最终MP4文件的地方
REMOVEOri = False  # 如果需要将源文件删除，将其更改为True
CUSTOM_DIR = False  # 是否自定义输入文件处理目录

errMsg = ['合并成功', '合并错误', '未读取到文件']


# 测试函数
def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.
    print(len([1, 2, 3, 4]))


# 过滤Windows文件名中的非法字符
def file_name_filter(file_name):
    invalid_chars = '[\\\/:*?？"<>|]'
    replace_char = ''
    filename = re.sub(invalid_chars, replace_char, file_name)
    return filename


# video.m4s和audio.m4s合并转换为MP4的核心代码
def convert_video():
    os.chdir(myDir)  # 改变当前的工作目录到指定的路径
    directory = os.getcwd()  # 返回当前工作目录
    print('directory -> ', directory)

    # os.listdir() 方法用于返回指定的文件夹包含的文件或文件夹的名字的列表
    # filter() 函数用于过滤序列，过滤掉不符合条件的元素，返回由符合条件元素组成的新列表。参数一：判断函数；参数二：需要处理的序列
    # list() 用于将元组转换为列表
    # 最外层的目录
    file_list = list(filter(os.path.isdir, os.listdir()))
    succeed_count = 0
    total_count = len(file_list)
    for videoNameDir in file_list:
        # F:\bilibiliVideoDLSmall\test\389864960
        video_main_dir = os.path.join(directory, videoNameDir)  # 把目录和文件名合成一个路径
        print('video_main_dir -> ', video_main_dir)
        os.chdir(video_main_dir)

        for cDir in list(filter(os.path.isdir, os.listdir())):
            # F:\bilibiliVideoDLSmall\test\389864960\1
            each_part_path = os.path.join(directory, videoNameDir, cDir)
            print('each_part_path -> ', each_part_path)

            # 从JSON文件中读取视频文件名称
            json_file_path = os.path.join(each_part_path, 'entry.json')
            print('json_file_path -> ', json_file_path)
            # 打开JSON文件
            file = open(json_file_path, 'rb')
            json_data = json.load(file)
            print(json_data)
            new_file_name = json_data['title']
            print('new_file_name -> ', new_file_name)
            file.close()  # 关闭文件
            os.chdir(each_part_path)  # reach 此视频主文件夹中的一个分p

            # 视频一般放在分p文件夹中的数字文件夹中，一般数字文件夹仅一个
            # 包含音频和视频的目录
            for digitFolder in list(filter(os.path.isdir, os.listdir())):
                # F:\bilibiliVideoDLSmall\test\389864960\1\80
                sep_path = os.path.join(directory, videoNameDir, cDir, digitFolder)
                print('sep_path -> ', sep_path)
                os.chdir(sep_path)  # reach 此视频主文件夹中的一个分p的数字文件夹

                new_name = new_file_name + '.mp4'
                print('new_name -> ', new_name)
                filtered_name = file_name_filter(new_name)  # 过滤Windows文件名中的非法字符
                print('filtered_name -> ', filtered_name)

                # 在此路径下调用cmd: ffmpeg -i video.m4s -i audio.m4s -codec copy output.mp4
                # subprocess 模块允许我们启动一个新进程，并连接到它们的输入/输出/错误管道，从而获取返回值：0代表正确执行，1和2都是错误执行，2通常是没有读取到文件
                ret = subprocess.call('ffmpeg -i video.m4s -i audio.m4s -codec copy output.mp4', shell=True)
                print('execute cmd result -> ', errMsg[ret])

                # output.mp4的绝对路径
                file_path_out_put_old_name = os.path.join(directory, videoNameDir, cDir, digitFolder, 'output.mp4')
                print('file_path_out_put_old_name -> ', file_path_out_put_old_name)
                if not os.path.exists(finalDir):  # 不存在则创建文件目录
                    os.makedirs(finalDir)
                file_path_out_put_new_name_with_new_path = os.path.join(finalDir, filtered_name)
                print('file_path_out_put_new_name_with_new_path -> ', file_path_out_put_new_name_with_new_path)

                if os.path.exists(file_path_out_put_new_name_with_new_path):
                    os.remove(file_path_out_put_new_name_with_new_path)  # 存在则删除文件
                    print('删除文件成功：', file_path_out_put_new_name_with_new_path)
                # 重命名文件或目录
                os.rename(file_path_out_put_old_name, file_path_out_put_new_name_with_new_path)
                succeed_count += 1

    print(f'文件批量合成完毕：{succeed_count}/{total_count}')
    # print('文件批量合成完毕：%d/%d' % (succeed_count, total_count))

    if REMOVEOri:
        # remove 源文件夹
        os.chdir(myDir)
        directory = os.getcwd()
        for videoNameDir in list(filter(os.path.isdir, os.listdir())):
            video_name_dir_path = os.path.join(directory, videoNameDir)
            # 递归删除一个目录及目录中的所有内容
            shutil.rmtree(video_name_dir_path)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print_hi('PyCharm')
    if CUSTOM_DIR:
        myDir = input('请输入源文件目录：')
        print(f'源文件目录为：{myDir}')
        finalDir = input('请输入目标文件目录：')
        print(f'目标文件目录为：{finalDir}')
    convert_video()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
