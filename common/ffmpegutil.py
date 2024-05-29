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
        # print('cmd_str-->', cmd_str)
        # ret = subprocess.call(cmd_str, shell=True)
        ret = subprocess.call(cmd_str, shell=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return ret, ''
    except Exception as e:
        return ret, e


# 取视频的第100帧-给视频添加封面
def add_local_cover(video_path):
    title = video_path.split('/')[-1]
    ori_path = video_path.split('.')[0]
    video_format = video_path.split('.')[1]
    temp_name = f'{ori_path}___without_cover.{video_format}'
    cover_img_name = f'{ori_path}_thumb.png'
    ret, err_msg = get_video_cover(video_path, cover_img_name)
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


if __name__ == '__main__':
    # video_name = 'F:/Video/Bilibili/2ciyuan/2024年5月13日004618/20240526.mp4'
    # video_name = 'F:/Video/Bilibili/2ciyuan/2024年5月13日004618/202405/20240513.mp4'
    # add_local_cover(video_name)
    # video_name = 'F:/Video/Bilibili/2ciyuan/2024年5月13日004618/202405/20240505_4.mp4'
    # video_dist_path = 'F:/Video/Bilibili/2ciyuan/2024年5月13日004618/202405/20240505__4.mp4'
    # thumb_path = 'F:/Video/Bilibili/2ciyuan/2024年5月13日004618/202405/20240505_4_pic.png'
    # add_cover_to_video(video_name, thumb_path, video_dist_path)

    video_name = 'E:/Video/Afun/k_2024年5月20日005857/据说是…先天‘柳如烟’圣体！？——▎大师精选¹¹⁶___without_cover.mp4'
    get_video_cover(video_name)
