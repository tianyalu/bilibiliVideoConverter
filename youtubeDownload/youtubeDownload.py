import os
from yt_dlp import YoutubeDL
from common import fileutil, utils, ffmpegutil, globaldata
from datetime import datetime

# 视频下载URL
DOWNLOAD_URL = 'https://www.youtube.com/watch?v=ZD5cVDPn1_k'
# 批量视频链接列表
VIDEO_URLS = [
  'https://www.youtube.com/watch?v=x2cyLa_Qjfs',
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


def get_cookies_options():
    """获取 cookies 配置选项"""
    cookies_options = {}
    
    # 尝试多种 cookies 文件路径
    cookies_paths = [
        './cookies.txt',
        './youtube_cookies.txt',
        '../cookies.txt',
        os.path.expanduser('~/cookies.txt')
    ]
    
    for path in cookies_paths:
        if os.path.exists(path):
            cookies_options['cookiefile'] = path
            print(f"✅ 找到 cookies 文件: {path}")
            break
    else:
        print("⚠️ 未找到 cookies 文件，尝试使用浏览器 cookies")
        # 尝试从浏览器获取 cookies
        try:
            cookies_options['cookiesfrombrowser'] = ('chrome',)
            print("✅ 使用 Chrome 浏览器 cookies")
        except:
            try:
                cookies_options['cookiesfrombrowser'] = ('firefox',)
                print("✅ 使用 Firefox 浏览器 cookies")
            except:
                print("❌ 无法获取浏览器 cookies，可能需要手动配置")
    
    return cookies_options


# 下载YouTube视频
# url: 视频链接
# download_cover: 是否下载封面并添加到视频
# format: 下载格式（如'best', 'bestvideo+bestaudio'等）
def singleDownloadVideo(url, downloadCover=True, format='bestvideo+bestaudio/best'):
    try:
        fileutil.create_directory(VIDEO_DIR)  # 确保目录存在
        
        # 获取 cookies 配置
        cookies_options = get_cookies_options()
        
        # 先获取视频信息
        temp_opts = {
            'quiet': True,
            'no_warnings': True,
            **cookies_options
        }
        
        try:
            with YoutubeDL(temp_opts) as ydl:
                info = ydl.extract_info(url, download=False)
        except Exception as e:
            if "Sign in to confirm your age" in str(e):
                print("❌ 需要年龄验证，请确保已正确配置 cookies")
                print("💡 解决方案:")
                print("   1. 在浏览器中登录 YouTube 并访问该视频")
                print("   2. 导出 cookies 到 cookies.txt 文件")
                print("   3. 或使用 --cookies-from-browser 选项")
                raise e
            else:
                raise e
        
        print(f"视频标题: {info.get('title', 'Unknown')}")
        print(f"视频格式: {info.get('ext', 'Unknown')}")
        print(f"视频时长: {info.get('duration', 'Unknown')}秒")
        
        # 根据原视频格式设置下载参数
        video_ext = info.get('ext', 'mp4')
        
        ydl_opts = {
            'format': format,
            'outtmpl': f'{VIDEO_DIR}/%(title)s_{datetime.now().strftime("%Y%m%d%H%M%S")}.%(ext)s',
            'noplaylist': True,
            'quiet': False,
            'writethumbnail': downloadCover,
            'writeinfojson': False,
            'writesubtitles': False,
            'writeautomaticsub': False,
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            },
            **cookies_options  # 添加 cookies 配置
        }
        
        if video_ext == 'webm':
            # webm 格式特殊处理
            ydl_opts['postprocessor_args'] = {
                'ffmpeg': [
                    '-c:v', 'copy',
                    '-c:a', 'copy',
                    '-avoid_negative_ts', 'make_zero',
                    '-f', 'webm'  # 强制 webm 格式
                ]
            }
            # webm 格式不支持嵌入缩略图，禁用以避免格式转换
            ydl_opts['postprocessors'] = []
            ydl_opts['writethumbnail'] = False  # 不下载缩略图
            print("检测到 webm 格式，已禁用缩略图下载以保持格式")
        else:
            # 其他格式使用通用参数
            ydl_opts['postprocessor_args'] = {
                'ffmpeg': [
                    '-c:v', 'copy',
                    '-c:a', 'copy',
                    '-avoid_negative_ts', 'make_zero'
                ]
            }
            # 其他格式可以嵌入缩略图
            ydl_opts['postprocessors'] = [
                {'key': 'EmbedThumbnail'} if downloadCover else {},
            ]
            ydl_opts['writethumbnail'] = downloadCover  # 根据参数决定是否下载缩略图
        
        # 使用设置好的参数下载视频
        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        print(f"下载完成: {url}")
            
    except Exception as e:
        print(f'下载失败: {e}')
        # 如果是合并失败，尝试手动处理
        if "merge" in str(e).lower() or "ffmpeg" in str(e).lower():
            print("检测到合并失败，尝试手动处理...")
            try_manual_merge(url, ydl_opts)


def try_manual_merge(url, ydl_opts):
    """手动处理音视频合并失败的情况"""
    try:
        # 修改配置，分别下载视频和音频，保持原格式
        manual_opts = ydl_opts.copy()
        manual_opts['format'] = 'bestvideo+bestaudio/best'
        # 移除强制格式转换
        # manual_opts['merge_output_format'] = 'mp4'
        
        with YoutubeDL(manual_opts) as ydl:
            ydl.download([url])
        print("手动合并成功")
    except Exception as e:
        print(f"手动合并也失败: {e}")


def batch_download_youtube(urls, downloadCover=True, format='bestvideo+bestaudio/best'):
    for i, url in enumerate(urls, 1):
        print(f'开始下载 [{i}/{len(urls)}]: {url}')
        try:
            singleDownloadVideo(url, downloadCover, format)
            print(f'下载成功 [{i}/{len(urls)}]')
        except Exception as e:
            print(f'下载失败 [{i}/{len(urls)}]: {e}')
        print('-' * 40)


if __name__ == '__main__':
    # with open('urls.txt', 'r', encoding='utf-8') as f:
    #     VIDEO_URLS = [line.strip() for line in f if line.strip()]
    batch_download_youtube(VIDEO_URLS)

