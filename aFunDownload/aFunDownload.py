"""
正常的视频：
    完整的视频数据 --> 直接下载
流媒体：
    视频数据 --> 分段 --> 每一段视频数据的url地址 --> 下载
    把完整的视频分成很多小段，每一段视频数据的url地址 ts文件
1. 通过分析网页源代码，找到视频的url地址
2. 通过requests模块发送请求，获取响应数据

3. 保存视频数据

进阶 ：获取一个up主的所有视频
    https://www.acfun.cn/u/56776847?quickViewId=ac-space-video-list&reqID=2&ajaxpipe=1&type=video&order=newest&page=1&pageSize=20&t=1705985425289

参考：https://blog.csdn.net/qq_34666239/article/details/136156691
"""

import requests  # 发送HTTP请求
import re  # 正则表达式库，用于文本匹配
from lxml import etree  # lxml:解析HTML内容  导入了 lxml 库的 etree 模块
import json  # 解析JSON数据
from tqdm import tqdm  # 在控制台显示进度条
from concurrent.futures import ThreadPoolExecutor, as_completed  # 提供异步执行的能力
import os
import pprint

# 1.确定url地址
URL = "https://www.acfun.cn/v/ac43577708"
# URL = 'https://www.acfun.cn/u/56776847?quickViewId=ac-space-video-list&reqID=2&ajaxpipe=1&type=video&order=newest&page=1&pageSize=20&t=1705985425289'
# 视频前缀     https://ali-safety-video.acfun.cn/mediacloud/acfun/acfun_video
PREFIX_URL = "https://ali-safety-video.acfun.cn/mediacloud/acfun/acfun_video/"


# 请求头，模拟浏览器访问
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 "
                  "Safari/537.36 "
}


# 第一步：分析视频页面
def get_video_info_and_title(url):
    # 2.发请求获取页面数据
    response = requests.get(url=url, headers=headers)
    response.encoding = "utf-8"
    html = response.text
    # print(html)
    # 3.解析数据，先找标题
    # 使用lxml和正则表达式解析HTML
    etree_html = etree.HTML(html)
    title = etree_html.xpath('//div[@class="video-description clearfix"]/h1/span/text()')  # 只有一个标题 使用xpath来取
    title = title[0] if (len(title) > 0) else '未定义的title'
    # 去除标题中的特殊字符
    title = re.sub(r"[\/\\\:\*\?\"\<\>\|]", "", title)  # 清理标题中的特殊字符
    # 再找视频的URL地址
    # re.S：标志参数，表示在匹配时考虑换行符。因为正则表达式中的 . 默认不匹配换行符
    videoInfo = re.findall(r"window.pageInfo= window.videoInfo = (.*?);", html, re.S)
    videoInfo = videoInfo[0] if (len(videoInfo) > 0) else '未定义的videoInfo'
    return videoInfo, title


# 第二步：解析视频数据
def parse_data(videoInfo):
    pprint(videoInfo)
    # 解析JSON数据
    ksPlayJson = json.loads(videoInfo)['currentVideo']['ksPlayJson']
    representation = json.loads(ksPlayJson)['adaptationSet'][0]['representation']
    backupUrl = representation[0]['backupUrl'][0]  # 视频的URL地址
    # 请求视频数据
    m3u8_data = requests.get(url=backupUrl, headers=headers)
    m3u8_data.encoding = 'utf-8'
    # 使用正则表达式找到所有的视频片段URL
    segments = re.findall(r",\n(.*?)\n#E", m3u8_data.text, re.S)
    return segments


# 下载视频
def download_video(segments, title, name):
    for item in tqdm(segments):
        # 拼接视频的URL地址
        m3u8_download_url = PREFIX_URL + item
        print(m3u8_download_url)
        # 下载视频数据
        video_get = requests.get(url=m3u8_download_url, headers=headers)
        if video_get.status_code != 200:
            pprint.pprint(f"{title}.mp4下载失败，丢失片段{m3u8_download_url}，状态码：{video_get.status_code}")
            continue
        else:
            video = video_get.content
            with open(f"file/video/{name}/{title}.mp4", 'ab') as f:
                f.write(video)
                print(f"下载完成 {title}.mp4")
                f.close()


# 第三步：下载视频片段
def download_segment(args):
    # 下载单个视频片段
    index, segment_url, video_dir, title = args
    temp_filename = f"{video_dir}/temp_{index:05d}.ts"
    try:
        response = requests.get(url=segment_url, headers=headers)
        if response.status_code == 200:
            with open(temp_filename, "wb") as f:
                f.write(response.content)
            return index, temp_filename
        else:
            return index, None
    except Exception as e:
        print(e)
        return index, None


# 合并所有视频片段
def merge_video_segments(segment_files, final_path):
    with open(final_path, 'wb') as final_file:  # 写入完成，文件会在 with 语句块退出时自动关闭，无需额外调用 close() 方法
        for segment_file in segment_files:
            with open(segment_file, 'rb') as f:
                final_file.write(f.read())
            os.remove(segment_file)  # 删除临时文件


# 第四步：并发下载和合并视频
def download_video_concurrently(segments, title, name):
    video_dir = f"file/video/{name}"
    if not os.path.exists(video_dir):
        os.makedirs(video_dir)
    final_path = f"{video_dir}/{title}.mp4"
    segment_urls = [segment_url for segment_url in segments]
    # 准备下载任务
    tasks = [(index, segment_url, video_dir, title) for index, segment_url in enumerate(segment_urls)]  # enumerate() 函数用于将一个可遍历的数据对象（如列表、元组或字符串）组合为一个索引序列，同时列出数据和数据下标
    # 存储临时文件名
    segment_files = [None] * len(segments)  # [None] * len(segments) 使用乘法操作符创建了一个包含 None 元素的列表，其长度等于 segments 列表的长度
    with ThreadPoolExecutor(max_workers=10) as executor:
        future_to_segment = {executor.submit(download_segment, task): task for task in tasks}
        for future in tqdm(as_completed(future_to_segment), total=len(segments), desc=f"下载视频片段：{title}"):
            index, temp_file = future.result()
            if temp_file:
                segment_files[index] = temp_file
    # 合并视频片段
    if all(segment_files):
        merge_video_segments(segment_files, final_path)
        print(f"视频合并完成：{final_path}")
    else:
        print("某些片段下载失败，视频可能不完整")


def main(url, name):
    # name为空的就传时间
    if name == '':
        name = "A站"
    videoInfo, title = get_video_info_and_title(url)
    findall = parse_data(videoInfo)
    download_video(findall, title, name)
    download_video_concurrently(findall, title, name)


if __name__ == '__main__':
    # print('PyCharm hhah哈哈哈 ')
    # (videoInfo, title) = get_video_info_and_title(URL)
    # print(f'videoInfo: {videoInfo}\n title: {title}')
    main(URL, '测试')
