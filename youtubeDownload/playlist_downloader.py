import os
import sys
import time
from yt_dlp import YoutubeDL
from datetime import datetime

# 添加项目根目录到 Python 路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 下载目录
VIDEO_DIR = 'E:/Video/YouTube/2025年7月18日004433'

def download_playlist_video_by_index(playlist_url, video_index=0, download_dir=None):
    """
    从播放列表中下载指定索引的视频
    
    Args:
        playlist_url: 播放列表URL
        video_index: 视频在播放列表中的索引（从0开始）
        download_dir: 下载目录，如果为None则使用默认目录
    """
    try:
        # 使用默认目录或指定目录
        if download_dir is None:
            download_dir = VIDEO_DIR
        
        # 确保下载目录存在
        os.makedirs(download_dir, exist_ok=True)
        
        print(f"🔍 获取播放列表信息: {playlist_url}")
        print(f"📥 准备下载第 {video_index + 1} 个视频")
        
        # 获取播放列表信息
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': True,  # 只获取基本信息，不下载
        }
        
        with YoutubeDL(ydl_opts) as ydl:
            playlist_info = ydl.extract_info(playlist_url, download=False)
        
        if not playlist_info or 'entries' not in playlist_info:
            print("❌ 无法获取播放列表信息")
            return False
        
        entries = playlist_info['entries']
        if video_index >= len(entries):
            print(f"❌ 播放列表只有 {len(entries)} 个视频，索引 {video_index} 超出范围")
            return False
        
        # 获取指定视频的信息
        target_video = entries[video_index]
        video_url = target_video.get('url') or f"https://www.youtube.com/watch?v={target_video.get('id')}"
        video_title = target_video.get('title', f'video_{video_index}')
        
        print(f"✅ 找到目标视频: {video_title}")
        print(f"🔗 视频链接: {video_url}")
        
        # 下载指定视频
        download_opts = {
            'format': 'bestvideo+bestaudio/best',
            'outtmpl': f'{download_dir}/%(title)s_{datetime.now().strftime("%Y%m%d%H%M%S")}.%(ext)s',
            'noplaylist': True,
            'quiet': False,
            'writethumbnail': True,
            'writeinfojson': False,
            'sleep_interval': 2,
            'max_sleep_interval': 10,
            'retries': 3,
            'fragment_retries': 3,
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            },
        }
        
        with YoutubeDL(download_opts) as ydl:
            ydl.download([video_url])
        
        print(f"✅ 下载完成: {video_title}")
        return True
        
    except Exception as e:
        print(f"❌ 下载失败: {e}")
        return False

def download_playlist_videos_by_indices(playlist_url, indices, download_dir=None):
    """
    从播放列表中下载多个指定索引的视频
    
    Args:
        playlist_url: 播放列表URL
        indices: 视频索引列表，如 [0, 2, 5]
        download_dir: 下载目录，如果为None则使用默认目录
    """
    # 使用默认目录或指定目录
    if download_dir is None:
        download_dir = VIDEO_DIR
    
    print(f"🎵 批量下载播放列表视频")
    print(f"📋 目标索引: {indices}")
    print(f"📁 下载目录: {download_dir}")
    print("=" * 50)
    
    success_count = 0
    for i, index in enumerate(indices):
        print(f"\n📥 下载第 {i+1}/{len(indices)} 个视频 (索引: {index})")
        if download_playlist_video_by_index(playlist_url, index, download_dir):
            success_count += 1
        
        # 添加延迟避免速率限制
        if i < len(indices) - 1:
            print("⏳ 等待 5 秒...")
            import time
            time.sleep(5)
    
    print(f"\n🎉 批量下载完成: {success_count}/{len(indices)} 个视频成功")

if __name__ == '__main__':
    # 示例用法
    playlist_url = 'https://www.youtube.com/playlist?list=RDnViyMVR_XG8'
    
    print(f"🎯 播放列表下载器")
    print(f"📁 默认下载目录: {VIDEO_DIR}")
    print("=" * 50)
    
    # 下载播放列表中的第1个视频（索引0）
    # download_playlist_video_by_index(playlist_url, 0)
    
    # 下载播放列表中的第1、3、5个视频
    download_playlist_videos_by_indices(playlist_url, [0, 2, 4])
    
    # 也可以指定自定义目录
    # download_playlist_videos_by_indices(playlist_url, [0, 2, 4], 'E:/Video/YouTube/custom_folder') 