# 91下载器

import binascii
import random

# pip install pycryptodome
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

import requests  # 发送HTTP请求
import re  # 正则表达式库，用于文本匹配
from lxml import etree  # lxml:解析HTML内容  导入了 lxml 库的 etree 模块
import json  # 解析JSON数据
from tqdm import tqdm  # 在控制台显示进度条
from concurrent.futures import ThreadPoolExecutor, as_completed  # 提供异步执行的能力
import os
import m3u8
import pprint
import time
from datetime import datetime
from common import logutil
from common import fileutil
from common import jsonutil
from common import globaldata
from common import const
from common import utils

VIDEO_DIR = 'G:\\video\\YouTube\\91\\2024年8月11日183009'
KEY_FILE = f'{VIDEO_DIR}/video.key'  # m3u8的秘钥文件
key = None
key_iv = None
# 单视频下载
URL = "https://i91.icu/2024/08/09/14336/"
# URL = "https://i91.icu/2024/02/08/8087/"
# URL = "https://91lt.co/2024/02/06/7821/"
# URL = "https://91lt.co/2024/02/02/7394/"

logging = logutil.init_logger('', 'error_log')

cookie = 'X_CACHE_KEY=39767f2676ad12e666d119baa1e75f3f; __vtins__KFmJPozWnvhqSgQd=%7B%22sid%22%3A%20%22ad76ced1-77dc-5ea7-a46f-0f206a4c15a0%22%2C%20%22vd%22%3A%201%2C%20%22stt%22%3A%200%2C%20%22dr%22%3A%200%2C%20%22expires%22%3A%201723542360495%2C%20%22ct%22%3A%201723540560495%7D; __51uvsct__KFmJPozWnvhqSgQd=1; __51vcke__KFmJPozWnvhqSgQd=25c71531-9d41-58d8-8b86-4e072a402335; __51vuft__KFmJPozWnvhqSgQd=1723540560498; showed_system_notice=showed'

# 请求头，模拟浏览器访问
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 "
                  "Safari/537.36 ",
    # ":authority": '91lt.co'

    # "Cookie": cookie,
    # "Referer": "https://91lt.co/",
    # "Sec-Ch-Ua": '"Not/A)Brand";v="8", "Chromium";v="126", "Google Chrome";v="126"',
    # "Sec-Ch-Ua-Platform": "Windows"
    # ":path": '/wp-admin/admin-ajax.php?action=search_box',
}


# 第一步：分析视频页面
def get_video_info_and_title(url):
    # 2.发请求获取页面数据
    # response = requests.get(url=url, headers=random.choice(const.headers_list))
    # response = fetch(url)
    response = requests.get(url=url, headers=headers)
    if response:
        response.encoding = "utf-8"
        html = response.text
        logging.error(html)
        # response.close()

    # 3.解析数据，先找标题
    # 使用lxml和正则表达式解析HTML
    etree_html = etree.HTML(html)
    # pprint.pprint(f'etree_html: {etree_html}')
    # //div 会选择所有 <div> 元素，而 div 只会选择当前上下文节点的直接子级中的 <div> 元素
    title = etree_html.xpath('//title/text()')  # 只有一个标题 使用xpath来取
    title = title[0] if (len(title) > 0) else '未定义的title'
    # 去除标题中的特殊字符
    title = re.sub(r"[\/\\\:\*\?\"\<\>\|\s]", "", title)  # 清理标题中的特殊字符
    delimiter = '91分享'
    if delimiter in title:
        title = title.split(delimiter)[0]
    # print(f'title-->{title}')

    # 再找视频的URL地址
    video_urls = etree_html.xpath('//div/@video-url')
    # print(f'video_urls: {video_urls}')
    if len(video_urls) == 0:
        print(f'视频地址获取失败：{title}')

    # 找图片urls
    # image_urls = etree_html.xpath('//figure[contains(@class, "wp-block-image")]//img/@data-src')
    image_urls = etree_html.xpath('//figure[@class="wp-block-image"]//img/@data-src')
    # print(f'image_urls: {image_urls}')
    if len(image_urls) == 0:
        print(f'未获取到图片url')

    return video_urls, image_urls, title


def download(page_url):
    video_urls, image_urls, title = get_video_info_and_title(page_url)
    if len(image_urls) > 0 or len(video_urls) > 0:
        video_path = os.path.join(VIDEO_DIR, title)
        # 确保录存在
        # os.makedirs(os.path.dirname(video_path), exist_ok=True)
        if len(image_urls) > 0:
            image_path = os.path.join(video_path, 'pic')
            # os.makedirs(os.path.dirname(image_path), exist_ok=True)
            download_images(image_urls, image_path)
        else:
            logging.error(f'图片地址获取失败：{title}')
            print(f'图片地址获取失败：{title}')

        if len(video_path) > 0:
            download_video(video_urls, video_path, title)
        else:
            logging.error(f'视频地址获取失败：{title}')
            print(f'视频地址获取失败：{title}')
    else:
        logging.error(f'视频图片地址均获取失败：{title}')
        print(f'视频图片地址均获取失败：{title}')


# 下载图片
def download_images(image_urls, image_path):
    print(f'图片下载中...')
    succeed = 0
    for url in image_urls:
        file_name = os.path.join(image_path, f'{url.split("/")[-1]}.jpg')
        ret = do_download_image(url, file_name)
        if ret:
            succeed += 1
    print(f'图片下载完毕({succeed}/{len(image_urls)})')


# 真正下载图片
def do_download_image(url, file_name):
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # 检查请求是否成功
        # 确保目录存在
        os.makedirs(os.path.dirname(file_name), exist_ok=True)
        # 将图片写入文件
        with open(file_name, 'wb') as file:
            file.write(response.content)
            return True
    except requests.RequestException as e:
        print(f'Error downloading image {file_name.split("./")[-1]}: {e}')
        return False


# 下载视频
def download_video(video_urls, video_path, title):
    print(f'视频【{title}】下载中...')
    # 下载视频
    if len(video_urls) == 1:
        video_name = f'{title}.mp4'
        output_file = os.path.join(video_path, video_name)
        do_download(video_urls[0], output_file)
    elif len(video_urls) > 1:
        for index, video_url in enumerate(video_urls, start=0):
            video_name = f'{title}{index}.mp4'
            output_file = os.path.join(video_path, video_name)
            do_download(video_urls[index], output_file)


def do_download(url, output_file):
    if url.endswith('m3u8'):
        download_m3u8(url, output_file)


# 下载m3u8视频
def download_m3u8(m3u8_url, output_file):
    # 确保输出目录存在
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    # 下载 m3u8 文件
    m3u8_obj = m3u8.load(m3u8_url)
    segments = m3u8_obj.segments
    # print(f'segments--> ', segments)
    # segment_urls = [segment.uri for segment in segments]
    segment_urls = [segment.absolute_uri for segment in segments]
    # print(f'segment_urls --> {segment_urls}')
    # 获取秘钥信息
    if m3u8_obj.keys:
        key_info = m3u8_obj.keys[0]  # 获取第一个秘钥信息
        global key, key_iv
        key_url = key_info.absolute_uri
        # print(f'key_url --> {key_url}')
        key_iv = binascii.unhexlify(key_info.iv[2:])
        # print(f'key_iv --> {key_iv}')
        download_key(key_url, KEY_FILE)
        with open(KEY_FILE, 'rb') as f:
            key = f.read()

    # 执行下载操作
    download_video_concurrently(segment_urls, output_file)


# 下载秘钥文件
def download_key(url, dest):
    response = requests.get(url)
    response.raise_for_status()
    with open(dest, 'wb') as f:
        f.write(response.content)
    return dest


# 下载视频片段
def download_segment(args):
    # 下载单个视频片段
    index, segment_url, title = args
    seg_url = segment_url if (segment_url.startswith('http')) else segment_url
    # print(f'seg_url: {seg_url}')
    temp_filename = f"{VIDEO_DIR}/temp_{index:05d}.ts"
    ret = do_download_segment(index, seg_url, temp_filename)
    if ret:
        return index, temp_filename
    else:
        return index, None


def do_download_segment(index, segment_url, temp_filename):
    try:
        # print(f'\nsegment url --> {segment_url}')
        response = requests.get(url=segment_url, headers=headers)
        if response.status_code == 200:
            with open(temp_filename, "wb") as f:
                f.write(response.content)
            return True
        else:
            return False
    except Exception as e:
        print(e)
        return False


# 解密文件
def decrypt_file(input_file, output_file):
    cipher = AES.new(key, AES.MODE_CBC, key_iv)
    with open(input_file, 'rb') as f:
        ciphertext = f.read()
    plaintext = unpad(cipher.decrypt(ciphertext), AES.block_size)
    with open(output_file, 'wb') as f:
        f.write(plaintext)


# 合并所有视频片段
def merge_video_segments(segment_files, final_path):
    with open(final_path, 'wb') as final_file:  # 写入完成，文件会在 with 语句块退出时自动关闭，无需额外调用 close() 方法
        for segment_file in segment_files:
            decrypted_file = f'{segment_file}_decrypted'
            decrypt_file(segment_file, decrypted_file)
            with open(decrypted_file, 'rb') as f:
                final_file.write(f.read())
            os.remove(segment_file)  # 删除临时文件
            os.remove(decrypted_file)  # 删除临时文件
        os.remove(KEY_FILE)


def download_video_concurrently(segments, final_name):
    start_time = time.time()
    title = final_name.split('/')[-1]
    segment_urls = [segment_url for segment_url in segments]
    # 准备下载任务
    tasks = [(index, segment_url, title) for index, segment_url in
             enumerate(segment_urls)]  # enumerate() 函数用于将一个可遍历的数据对象（如列表、元组或字符串）组合为一个索引序列，同时列出数据和数据下标
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
        merge_video_segments(segment_files, final_name)
        end_time = time.time()
        print(f"视频合并完成({len(segment_files)}/{len(segments)})：{title}")
        print(f"用时：{end_time - start_time} S")
    else:
        print("某些片段下载失败，视频可能不完整")


def fetch(url):
    session = requests.Session()
    retry = Retry(total=3, backoff_factor=0.1, status_forcelist=[500, 502, 503, 504])
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)

    response = None
    try:
        response = session.get(url)
        print(response.text)
    except requests.exceptions.RequestException as e:
        print(e)
        logging.error(f'请求url【{url}】失败: {e}')
    return response


if __name__ == '__main__':
    # get_video_info_and_title(URL)
    # download_video(URL)
    # get_video_info_and_title('https://d1vryrtjfsdwoa.cloudfront.net/video/2024-02-02/15/1753326084635242496/864cb2edc17d4550ad8863fd3586116b.m3u8')
    download(URL)

