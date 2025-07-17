import os
from yt_dlp import YoutubeDL
from common import ffmpegutil

# 视频页面地址
VIDEO_URL = 'https://www.iwara.tv/video/eovybuo7y3uvr2abz'
# 视频链接列表
VIDEO_URLS = [
    'https://www.iwara.tv/video/eovybuo7y3uvr2abz',
    # 其它视频链接...
]
# 下载目录
VIDEO_DIR = 'E:/Video/Iwara'


def download_iwara_video(url):
    # 确保下载目录存在
    if not os.path.exists(VIDEO_DIR):
        os.makedirs(VIDEO_DIR)
    # yt-dlp 配置
    ydl_opts = {
        'format': 'bestvideo+bestaudio/best',
        'outtmpl': f'{VIDEO_DIR}/%(title)s.%(ext)s',
        'merge_output_format': 'mp4',
        'cookiefile': './cookies.txt',  # 如需登录请导出 cookies
        'quiet': False,
        'noplaylist': True,
        'writethumbnail': True,  # 下载缩略图
        'postprocessors': [
            {'key': 'FFmpegVideoConvertor', 'preferedformat': 'mp4'},
            {'key': 'EmbedThumbnail'},  # 自动嵌入缩略图
        ],
    }
    try:
        with YoutubeDL(ydl_opts) as ydl:
            result = ydl.extract_info(url, download=True)
            # 检查是否有封面
            video_title = result.get('title', 'video')
            video_path = os.path.join(VIDEO_DIR, f"{video_title}.mp4")
            # 检查是否嵌入了封面
            if not result.get('thumbnail'):
                # 没有封面，自动用本地帧生成封面
                if os.path.exists(video_path):
                    code, msg = ffmpegutil.add_local_cover(video_path)
                    if code == 0:
                        print('已自动添加本地封面')
                    else:
                        print(f'添加本地封面失败: {msg}')
                else:
                    print('未找到视频文件，无法添加本地封面')
    except Exception as e:
        print(f'下载失败: {e}')


def batch_download_iwara(urls):
    for url in urls:
        print(f'开始下载: {url}')
        download_iwara_video(url)
        print('-' * 40)


if __name__ == '__main__':
    # with open('urls.txt', 'r', encoding='utf-8') as f:
    #   VIDEO_URLS = [line.strip() for line in f if line.strip()]
    batch_download_iwara(VIDEO_URLS)
