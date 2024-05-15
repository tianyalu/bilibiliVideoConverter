"""
参考：https://blog.csdn.net/cdl3/article/details/134362738
    https://www.jianshu.com/p/ff90b4e741b4
"""
import os

import requests
import json
import re
from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.audio.io.AudioFileClip import AudioFileClip
import logging


# URL = "https://www.bilibili.com/video/BV17w411C7M8"
# URL = "https://www.bilibili.com/video/BV1Zt421u7VT"
URL = "https://www.bilibili.com/video/BV1nb421B7Y5"

VIDEO_DIR = 'E:/Video/Bilibili/dq_dd'

cookie = "buvid3=693E5D64-D6EE-4D0B-80EF-6B8FB311E49F148830infoc; LIVE_BUVID=AUTO8616320601473568; i-wanna-go-back=-1; buvid_fp_plain=undefined; DedeUserID=252762452; DedeUserID__ckMd5=0ad182b5ba8cd810; is-2022-channel=1; buvid4=7F27D907-4425-A1B4-D0F0-BCBC4AC99D4F94660-022012501-Pk1O31qDhl5PJxZ%2B7vuTsYB%2BMly4g4IVhgTX7xBfK3joNTQcdUamlg%3D%3D; CURRENT_FNVAL=4048; rpdid=0zbfAHVOop|dVRInCuA|289|3w1OVm6C; hit-new-style-dyn=1; FEED_LIVE_VERSION=V8; fingerprint=a69a2a8a93d89dc81205dd8315010014; _uuid=52C21A1F-64104-EBCA-38FD-8ABAAF7510AC999187infoc; header_theme_version=CLOSE; enable_web_push=DISABLE; b_nut=100; home_feed_column=5; hit-dyn-v2=1; SESSDATA=58a4b88a%2C1729782271%2Cc9c6b%2A42CjAzLYJtgDK4e7LCoQTVlRf59JOkaWSvHw20x0JhKCT4lmBIiN_bBl_CeKh_qtfsC3ESVkpwUFFkLXpfck5CZmlqQktQZy1fTlVVdHZMWUMyZ3RtU2FBa1RtTEc4NHJNZWJka0g1OVhfU2FxTmYxaldITnVTLVcybUNCQjd1clc1NGdFamwyYWF3IIEC; bili_jct=d694439cd5c5a3688a3955c300ea32e9; bp_video_offset_252762452=925104301653622825; CURRENT_QUALITY=80; bili_ticket=eyJhbGciOiJIUzI1NiIsImtpZCI6InMwMyIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3MTU3OTI2OTIsImlhdCI6MTcxNTUzMzQzMiwicGx0IjotMX0.K36c_Pi9Y0sO5heX7deHmTY4rL9pUSTtk3Qpu98YNg0; bili_ticket_expires=1715792632; browser_resolution=1532-682; buvid_fp=4b512659c0c2362b192d58be59f61871; sid=4up5bt3l; bp_t_offset_252762452=931773187569483783; b_lsid=39997857_18F7CC6D6D9; PVID=1"
headers = {
    'Referer': 'https://www.bilibili.com/',  # 防盗链
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
    'Cookie': cookie
}

logging.basicConfig(filename='error_log.txt', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')


def get_bilibili_video_url(url):
    response = requests.get(url=url, headers=headers)
    html = response.text
    # print(html)
    # logging.error(html)

    # 使用正则提取标题
    titles = re.findall(r'<title data-vue-meta="true">(.*?)_哔哩哔哩_bilibili</title>', html, re.S)
    title = titles[0] if(len(titles) > 0) else '未定义标题'
    # 去除标题中的特殊字符
    title = re.sub(r"[\/\\\:\*\?\"\<\>\|]", "", title)  # 清理标题中的特殊字符
    print(f'B站视频标题：{title}')

    # 使用正则表达式提取视频信息
    # match_result = re.search(r'__playinfo__=(.*?)</script>', html)
    match_result = re.findall(r'__playinfo__=(.*?)</script>', html, re.S)
    match_result = match_result[0] if(len(match_result) > 0) else ''
    logging.error(match_result)
    if match_result:
        # print(match_result)
        play_info_dict = json.loads(match_result)
        # 获取视频下载链接
        dash_info = play_info_dict['data']['dash']
        # dash_info = match_result['data']['dash']
        video_info = dash_info['video'][2]
        audio_info = dash_info['audio'][2]

        video_url = video_info['base_url']
        audio_url = audio_info['base_url']

        # video_url = video_info['baseUrl']
        # audio_url = audio_info['baseUrl']

        # video_url = video_info['backupUrl'][0]
        # audio_url = audio_info['backupUrl'][0]

        return title, video_url, audio_url
    else:
        print('无法解析视频信息')
        return '', ''


def single_download_video(url):
    title, video_url, audio_url = get_bilibili_video_url(url)
    print(f'B站视频标题：{title}')
    print(f'B站视频下载地址：{video_url}')
    print(f'B站音频下载地址：{audio_url}')
    if video_url == '':
        return

    # 下载视频和音频
    video_content = requests.get(url=video_url, headers=headers).content
    audio_content = requests.get(url=audio_url, headers=headers).content
    # 保存视频和音频到本地
    with open('video.mp4', 'wb') as f1:
        f1.write(video_content)
    with open('audio.mp3', 'wb') as f2:
        f2.write(audio_content)
    # 加载视频和音频，合并为一个MP4文件
    video_clip = VideoFileClip('video.mp4')
    audio_clip = AudioFileClip('audio.mp3')
    final_video_clip = video_clip.set_audio(audio_clip)
    # 创建目录
    create_directory(VIDEO_DIR)
    final_path = f'{VIDEO_DIR}/{title}.mp4'
    final_video_clip.write_videofile(final_path)


def create_directory(directory_path):
    try:
        if not os.path.exists(directory_path):
            os.makedirs(directory_path)
            print(f"目录'{directory_path}'已创建")
        else:
            print(f"目录'{directory_path}'已存在")
    except Exception as e:
        print(f"创建目录时发生错误：{e}")


if __name__ == '__main__':
    single_download_video(URL)