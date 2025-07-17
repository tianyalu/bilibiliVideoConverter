import os
from yt_dlp import YoutubeDL
from common import fileutil, utils, ffmpegutil, globaldata
from datetime import datetime

# 视频下载URL
DOWNLOAD_URL = 'https://www.youtube.com/watch?v=ZD5cVDPn1_k'
# 批量视频链接列表
VIDEO_URLS = [
  'https://www.youtube.com/watch?v=ZD5cVDPn1_k',
  # 其它视频链接...
]
# 下载目录
VIDEO_DIR = 'E:/Video/YouTube/w_2024年9月22日154452'


def get_file_name(title):
    fileutil.create_directory(VIDEO_DIR)
    cur_time = datetime.now()
    time_str = cur_time.strftime("%m%d%H%M%S")
    title = utils.file_name_filter(title)
    final_name = f"{VIDEO_DIR}/{title}_{time_str}.mp4"
    return final_name


# 下载YouTube视频
# url: 视频链接
# download_cover: 是否下载封面并添加到视频
# format: 下载格式（如'best', 'bestvideo+bestaudio'等）
def singleDownloadVideo(url, downloadCover=True, format='bestvideo+bestaudio/best'):
    ydl_opts = {
        'format': format,
        'outtmpl': f'{VIDEO_DIR}/%(title)s_{datetime.now().strftime("%Y%m%d%H%M%S")}.%(ext)s',  # 指定输出目录
        'noplaylist': True,
        'quiet': False,
        'merge_output_format': 'mp4',
        'writethumbnail': downloadCover,
        'writeinfojson': False, # 不写入info.json文件
        'writesubtitles': False,
        'writeautomaticsub': False,
        'cookiefile': './cookies.txt',
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        },
        'postprocessors': [
            {'key': 'FFmpegVideoConvertor', 'preferedformat': 'mp4'},
            {'key': 'EmbedThumbnail'} if downloadCover else {},
        ],
    }
    try:
        fileutil.create_directory(VIDEO_DIR)  # 确保目录存在
        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
    except Exception as e:
        print(f'下载失败: {e}')


def batch_download_youtube(urls, downloadCover=True, format='bestvideo+bestaudio/best'):
    for url in urls:
        print(f'开始下载: {url}')
        singleDownloadVideo(url, downloadCover, format)
        print('-' * 40)


if __name__ == '__main__':
    # with open('urls.txt', 'r', encoding='utf-8') as f:
    #     VIDEO_URLS = [line.strip() for line in f if line.strip()]
    batch_download_youtube(VIDEO_URLS)

