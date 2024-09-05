import subprocess
import os


# 截取视频的第n帧并保存为图片
def get_video_cover(video_path, cover_img_path='thumb.png', n=100):
    ret = -1
    try:
        cmd_str = f'ffmpeg -i "{video_path}" -vf "select=eq(n\,{n})" -vframes 1 "{cover_img_path}"'
        # print('cmd_str-->', cmd_str)
        # ret = subprocess.call(cmd_str, shell=True)
        ret = subprocess.call(cmd_str, shell=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return ret, 'success'
    except Exception as e:
        return ret, e


# 给视频添加封面
def add_cover_to_video(video_path_src, cover_url, video_path_dist):
    ret = -1
    try:
        cmd_str = f'ffmpeg -i "{video_path_src}" -i "{cover_url}" -map 0 -map 1 -c copy -c:v:1 png -disposition:v:1 attached_pic "{video_path_dist}"'
        # cmd_str = f'ffmpeg -i "{video_path_src}" -i "{cover_url}" -map 0:v:0 -map 0:a:0 -map 0:v:2 -map 1:v:0 -c copy "{video_path_dist}"'
        # print('cmd_str-->', cmd_str)
        # ret = subprocess.call(cmd_str, shell=True)
        ret = subprocess.call(cmd_str, shell=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        # print(f'ret --> {ret}')
        return ret, ''
    except Exception as e:
        # print(e)
        return ret, e


# 取视频的第100帧-给视频添加封面
def add_local_cover(video_path):
    title = video_path.split('/')[-1]
    ori_path = video_path.split('.')[0]
    video_format = video_path.split('.')[1]
    temp_name = f'{ori_path}___without_cover.{video_format}'
    cover_img_name = f'{ori_path}_thumb.png'
    ret, err_msg = get_video_cover(video_path, cover_img_name, 200)
    if ret == 0:
        # 原文件先重命名为临时文件
        os.rename(video_path, temp_name)
        code, err_msg = add_cover_to_video(temp_name, cover_img_name, video_path)
        if code == 0:
            print(f'{title} 添加本地封面图成功')
            os.remove(cover_img_name)
            os.remove(temp_name)
            return code, 'success'
        else:
            print(f'{title} 添加本地封面图时出错 -> ', err_msg)
            if os.path.exists(video_path):
                os.remove(video_path)
            os.rename(temp_name, video_path)  # 出错后还原原文件名
            return code, err_msg
    else:
        print(f'{title} 获取本地封面图时出错 -> ', err_msg, ret)
        return ret, err_msg


# 通过cover_url-给视频添加封面
def add_remote_cover(video_path, cover_url):
    title = video_path.split('/')[-1]
    ori_path = video_path.split('.')[0]
    video_format = video_path.split('.')[1]
    temp_name = f'{ori_path}___without_cover.{video_format}'
    # 原文件先重命名为临时文件
    os.rename(video_path, temp_name)
    code, err_msg = add_cover_to_video(temp_name, cover_url, video_path)
    if code == 0:
        print(f'{title} 添加网络封面图成功')
        os.remove(temp_name)
        return code, 'success'
    else:
        print(f'{title} 添加网络封面图时出错 -> ', err_msg)
        if os.path.exists(video_path):
            os.remove(video_path)
        os.rename(temp_name, video_path)  # 出错后还原原文件名
        return code, err_msg


# 为一个目录下的所有视频批量添加本地封面图
def batch_add_local_cover(video_path):
    files = os.listdir(video_path)
    total = len(files)
    succeed_count = 0
    for file in files:
        fileName = os.path.join(video_path, file)
        code, msg = add_local_cover(fileName)
        if code == 0:
            succeed_count += 1
        else:
            print(f'{file} 添加封面失败：{msg}')
    print(f'添加封面图完成：{succeed_count}/{total}')


# 合并video.m4s 和 audio.m4s
def single_convert_video(video_path, audio_path, dist_name='output.mp4'):
    ret = -1
    try:
        cmd_str = f'ffmpeg -i {video_path} -i {audio_path} -codec copy {dist_name}'
        # print('cmd_str-->', cmd_str)
        # ret = subprocess.call(cmd_str, shell=True)
        ret = subprocess.call(cmd_str, shell=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return ret, ''
    except Exception as e:
        return ret, e


# 从视频文件中分离出音频
def split_audio_from_video(video_path, dist_name='output.mp3'):
    ret = -1
    try:
        """
        -i input.mp4: 指定输入文件
        -vn: 禁用视频流。这个参数告诉 ffmpeg 不要处理视频部分，只处理音频。
        -acodec copy: 指定音频编解码器为复制（copy），这样可以保持原始音频流的编解码格式和质量，而不进行重新编码。
        output_audio.aac: 指定输出文件的名称和格式。这里输出为 AAC 格式的音频文件 output_audio.aac，你可以根据需要选择其他格式，如 MP3 (output_audio.mp3) 等。
        """
        cmd_str = f'ffmpeg -i {video_path} -vn -acodec copy {dist_name}'
        # print('cmd_str-->', cmd_str)
        ret = subprocess.call(cmd_str, shell=True)
        # ret = subprocess.call(cmd_str, shell=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return ret, ''
    except Exception as e:
        return ret, e


# 将ts文件转换为mp4格式
def convert_ts_to_mp4(video_path, dist_name='output.mp4'):
    ret = -1
    try:
        cmd_str = f'ffmpeg -i {video_path} -c copy {dist_name}'
        # print('cmd_str-->', cmd_str)
        ret = subprocess.call(cmd_str, shell=True)
        # ret = subprocess.call(cmd_str, shell=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return ret, ''
    except Exception as e:
        return ret, e


# 将audio.m4s文件转换为mp3格式
def convert_m4s_to_mp3(audio_path, dist_name='output.mp3'):
    ret = -1
    try:
        cmd_str = f'ffmpeg -i "{audio_path}" "{dist_name}"'
        # print('cmd_str-->', cmd_str)
        ret = subprocess.call(cmd_str, shell=True)
        # ret = subprocess.call(cmd_str, shell=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return ret, ''
    except Exception as e:
        return ret, e


if __name__ == '__main__':
    # video_name = 'F:/Video/Bilibili/2ciyuan/2024年8月5日231428/Snapping - Bronya/4K小恶魔.mp4'
    # video_name = 'F:/Video/Bilibili/2ciyuan/2024年5月13日004618/菜鸡的作品5/20240528_2.mp4'
    # video_name = 'F:/Video/Bilibili/2ciyuan/2024年6月23日181625/202406'
    # add_local_cover(video_name)

    # batch_add_local_cover(video_name)
    # video_name = 'F:/Video/Bilibili/2ciyuan/2024年5月13日004618/202405/20240505_4.mp4'
    # video_dist_path = 'F:/Video/Bilibili/2ciyuan/2024年5月13日004618/202405/20240505__4.mp4'
    # thumb_path = 'F:/Video/Bilibili/2ciyuan/2024年5月13日004618/202405/20240505_4_pic.png'
    # add_cover_to_video(video_name, thumb_path, video_dist_path)

    # video_name = 'E:/Video/Afun/k_2024年5月20日005857/据说是…先天‘柳如烟’圣体！？——▎大师精选¹¹⁶___without_cover.mp4'
    # get_video_cover(video_name)

    # 合并音频和视频
    # video_name = 'E:/Video/Bilibili/testsrc/226622104/c_1068319711/80/video.m4s'
    # audio_name = 'E:/Video/Bilibili/testsrc/226622104/c_1068319711/80/audio.m4s'
    # dist_name = 'E:/Video/Bilibili/testsrc/226622104/c_1068319711/80/output.mp4'
    # single_convert_video(video_name, audio_name, dist_name)

    # 从视频中分离音频
    # video_name = 'E:/Video/Bilibili/testsrc/226622104/c_1068319711/80/output.mp4'
    # dist_name = 'E:/Video/Bilibili/testsrc/226622104/c_1068319711/80/output.aac'
    # ret, err_msg = split_audio_from_video(video_name, dist_name)
    # if ret != 0:
    #     print(err_msg)

    # 将ts转换为mp4
    # src_path = 'G:/video/YouTube/91/2024年8月11日183009/test'
    # dist_name = 'G:/video/YouTube/91/2024年8月11日183009/test1.mp4'
    # ret, err_msg = convert_ts_to_mp4(src_path, dist_name)
    # if ret != 0:
    #     print(err_msg)

    # 将audio.m4s转为mp3
    audio_name = 'C:/Users/tian/Desktop/113038455736150/c_25618025265/80/audio.m4s'
    dist_name = 'C:/Users/tian/Desktop/壁上观 张晓涵 +1.13倍速 升调 混音.mp3'
    ret, err_msg = convert_m4s_to_mp3(audio_name, dist_name)
