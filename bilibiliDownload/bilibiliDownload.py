"""
参考：https://blog.csdn.net/cdl3/article/details/134362738
"""


import requests
import json
import re
from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.audio.io.AudioFileClip import AudioFileClip

URL = "https://www.bilibili.com/video/BV17w411C7M8"


def get_bilibili_video_url(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    response = requests.get(url=url, headers=headers)
    html = response.text
    # print(html)

    # 使用正则表达式提取视频信息
    match_result = re.search(r'__playinfo__=(.*?)</script>', html)
    # match_result = re.findall(r'__playinfo__=(.*?)</script>', html, re.S)
    # match_result = match_result[0] if(len(match_result) > 0) else ''
    if match_result:
        print(match_result)
        play_info_str = match_result.group(1)
        play_info_dict = json.loads(play_info_str)
        # 获取视频下载链接
        dash_info = play_info_dict['data']['dash']
        video_info = dash_info['video'][0]
        audio_info = dash_info['audio'][0]

        video_url = video_info['base_url']
        audio_url = audio_info['base_url']

        return video_url, audio_url
    else:
        print('无法解析视频信息')
        return '', ''


def single_download_video(url):
    video_url, audio_url = get_bilibili_video_url(url)
    print(f'B站视频下载地址：{video_url}')
    print(f'B站音频下载地址：{audio_url}')
    if video_url == '':
        return

    # 下载视频和音频
    video_content = requests.get(video_url).content
    audio_content = requests.get(audio_url).content
    # 保存视频和音频到本地
    with open('video.mp4', 'wb') as f1:
        f1.write(video_content)
    with open('audio.mp3', 'wb') as f2:
        f2.write(audio_content)
    # 加载视频和音频，合并为一个MP4文件
    video_clip = VideoFileClip('video.mp4')
    audio_clip = AudioFileClip('audio.mp3')
    final_video_clip = video_clip.set_audio(audio_clip)
    final_video_clip.write_videofile('final.mp4')


if __name__ == '__main__':
    single_download_video(URL)