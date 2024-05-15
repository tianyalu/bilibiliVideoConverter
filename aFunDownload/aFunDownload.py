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
import time
import logging

# 1.确定url地址

# 单视频下载
# URL = "https://www.acfun.cn/v/ac43577708"
# URL = "https://m.acfun.cn/v/?ac=44523314&sid=d75e7106fb456c95"
# URL = "https://m.acfun.cn/v/?ac=44523314"
URL = "https://www.acfun.cn/v/ac35582241"
# URL = 'https://www.acfun.cn/u/56776847?quickViewId=ac-space-video-list&reqID=2&ajaxpipe=1&type=video&order=newest&page=1&pageSize=20&t=1705985425289'
# 视频前缀
PREFIX_URL = "https://ali-safety-video.acfun.cn/mediacloud/acfun/acfun_video"

# 批量下载（下载一个up主的所有视频）
# 批量下载的URL
BATCH_URL = "https://www.acfun.cn/u/56776847"
BATCH_FAV_URL = "https://www.acfun.cn/member/favourite/folder/74420975"
# 视频前缀
PREFIX_BATCH_URL = "https://www.acfun.cn"

# VIDEO_DIR = 'file/video'
VIDEO_DIR = 'E:/Video/Afun/j_2024年5月15日005857'

logging.basicConfig(filename='error_log.txt', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

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
    # pprint.pprint(f'html: {html}')
    # logging.error(html)

    # 3.解析数据，先找标题
    # 使用lxml和正则表达式解析HTML
    etree_html = etree.HTML(html)
    # pprint.pprint(f'etree_html: {etree_html}')
    # //div 会选择所有 <div> 元素，而 div 只会选择当前上下文节点的直接子级中的 <div> 元素
    title = etree_html.xpath('//div[@class="video-description clearfix"]/h1/span/text()')  # 只有一个标题 使用xpath来取
    title = title[0] if (len(title) > 0) else '未定义的title'
    print(f'title-->{title}')
    # 去除标题中的特殊字符
    title = re.sub(r"[\/\\\:\*\?\"\<\>\|]", "", title)  # 清理标题中的特殊字符
    # 再找视频的URL地址
    # re.S：标志参数，表示在匹配时考虑换行符。因为正则表达式中的 . 默认不匹配换行符
    videoInfo = re.findall(r"window.pageInfo = window.videoInfo = (.*?);", html, re.S)
    videoInfo = videoInfo[0] if (len(videoInfo) > 0) else '未定义的videoInfo'
    if not is_valid_json(videoInfo):
        print('JSON 非法')
        videoInfo = get_video_info_again(html)
    print(videoInfo)

    # logging.error('alkfdjadsl')
    logging.error(videoInfo)
    return videoInfo, title


def get_video_info_again(text):
    # 定义正则表达式模式
    pattern = r'window\.pageInfo\s*=\s*window\.videoInfo\s*=\s*({.*?})'
    # 使用 re.findall() 提取匹配的内容
    matches = re.findall(pattern, text)
    # print(matches)
    matches = matches[0] if (len(matches) > 0) else '未定义的videoInfo'
    return matches


# 第二步：解析视频数据
def parse_data(videoInfo):
    # 解析JSON数据
    ksPlayJson = json.loads(videoInfo)['currentVideoInfo']['ksPlayJson']
    # print(ksPlayJson)
    representation = json.loads(ksPlayJson)['adaptationSet'][0]['representation']
    backupUrl = representation[0]['backupUrl'][0]  # 视频的URL地址
    # 请求视频数据
    m3u8_data = requests.get(url=backupUrl, headers=headers)
    m3u8_data.encoding = 'utf-8'
    print(m3u8_data.text)
    # 使用正则表达式找到所有的视频片段URL
    segments = re.findall(r",\n(.*?)\n#E", m3u8_data.text, re.S)
    return segments


# 下载视频
def download_video(segments, title, name):
    start_time = time.time()
    total_segment = 0
    for item in tqdm(segments):
        # 拼接视频的URL地址
        m3u8_download_url = f'{PREFIX_URL}/{item}'
        print(m3u8_download_url)
        # 下载视频数据
        video_get = requests.get(url=m3u8_download_url, headers=headers)
        if video_get.status_code != 200:
            pprint.pprint(f"{title}.mp4下载失败，丢失片段{m3u8_download_url}，状态码：{video_get.status_code}")
            continue
        else:
            total_segment += 1
            video_dir = f"{VIDEO_DIR}/{name}" if name else VIDEO_DIR
            if not os.path.exists(video_dir):
                os.makedirs(video_dir)
            video = video_get.content
            with open(f"{video_dir}/{title}.mp4", 'ab') as f:  # append binary
                f.write(video)
                f.close()
    end_time = time.time()
    print(f"下载完成 {title}.mp4 \n完成率：{total_segment}/{len(segments)}")
    print(f'用时：{end_time - start_time} S')


# 第三步：下载视频片段
def download_segment(args):
    # 下载单个视频片段
    index, segment_url, video_dir, title = args
    segment_url = segment_url if (segment_url.startswith('http')) else f'{PREFIX_URL}/{segment_url}'
    temp_filename = f"{video_dir}/temp_{index:05d}.ts"
    try:
        print(f'\nsegment url --> {segment_url}')
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
    start_time = time.time()
    video_dir = f"{VIDEO_DIR}/{name}" if name else VIDEO_DIR
    if not os.path.exists(video_dir):
        os.makedirs(video_dir)
    final_path = f"{video_dir}/{title}.mp4"
    segment_urls = [segment_url for segment_url in segments]
    # 准备下载任务
    tasks = [(index, segment_url, video_dir, title) for index, segment_url in
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
        merge_video_segments(segment_files, final_path)
        end_time = time.time()
        print(f"视频合并完成({len(segment_files)}/{len(segments)})：{final_path}")
        print(f"用时：{end_time - start_time} S")
    else:
        print("某些片段下载失败，视频可能不完整")


def single_download_video(url, name='', isConcurrently=True):
    videoInfo, title = get_video_info_and_title(url)
    findall = parse_data(videoInfo)
    if isConcurrently:
        download_video_concurrently(findall, title, name)
    else:
        download_video(findall, title, name)


def test():
    html = "<div class='video-description clearfix'><h1 " \
           'class="title"><span>【温】全皮肤盛宴_(:з」∠)_你喜欢的我都有！</span></h1><div> '
    etree_html = etree.HTML(html)
    # pprint.pprint(f'etree_html --> {etree_html}')
    # nodes_with_class = etree_html.xpath("//div[@class='video-description clearfix']")
    title = etree_html.xpath('//div[@class="video-description clearfix"]/h1/span/text()')
    # pprint.pprint(f'title --> {title}')
    title = title[0] if (len(title) > 0) else '未定义的title'
    print(f'title --> {title}')


# 判断JSON是否合法
def is_valid_json(json_str):
    try:
        json.loads(json_str)
        return True
    except json.JSONDecodeError:
        return False


# 目录不存在时创建目录
def create_directory(directory_path):
    try:
        if not os.path.exists(directory_path):
            os.makedirs(directory_path)
            print(f"目录'{directory_path}'已创建")
        else:
            print(f"目录'{directory_path}'已存在")
    except Exception as e:
        print(f"创建目录时发生错误：{e}")


# 批量下载up主的视频，如果第二个参数>0, 则只截取第一页的前slice_count个视频下载
def batch_download_upper_video(batch_url, slice_count=0):
    # 把所有的视频URL放到一个列表中
    all_video_url = []
    # 发请求获取页面数据
    requests_get = requests.get(url=batch_url, headers=headers)
    requests_get.encoding = "utf-8"
    html = requests_get.text
    print(html)
    # 解析数据
    # 先找up主的名字和视频数量以及视频的URL地址
    etree_html = etree.HTML(html)
    # 视频总数量
    num = etree_html.xpath("//li[@class='active']/span/text()")
    num = num[0] if (len(num) > 0) else 0
    # up主的名字
    name = etree_html.xpath("//span[@class='text-overflow name']/text()")
    name = name[0] if (len(name) > 0) else '未定义的up主名称'
    print(f"up主的名字：{name}，视频总数量：{num}")

    # 找到视频的URL地址
    hrefs = etree_html.xpath("//div[@id='ac-space-video-list']/a/@href")
    # 先装第一页的视频URL地址
    all_video_url = [PREFIX_BATCH_URL + href for href in hrefs]
    all_video_url = list(set(all_video_url))  # 去重

    # 截取前slice_count个视频下载
    if slice_count > 0:
        all_video_url = all_video_url[:slice_count]
    else:
        # 找到下一页的url地址，根据num判断页数 一页20个视频
        # 页数
        page = int(num) // 20 + 1
        # 下一页的URL地址
        for i in range(2, page + 1):  # 从第二页开始，因为第一页已经装了
            # 获取当前时间戳
            current_timestamp = time.time()
            next_url = batch_url + f"?quickViewId=ac-space-video-list&reqID={i}&ajaxpipe=1&type=video&order=newest&page={i}&pageSize=20&t={current_timestamp}"
            print(next_url)
            # 发请求获取页面数据
            requests_get = requests.get(url=next_url, headers=headers)
            requests_get.encoding = 'utf-8'
            html = requests_get.text
            # 解析数据 使用正则
            hrefs = re.findall(r'href=\\"(.*?)"', html, re.S)
            for href in hrefs:
                # href /v/ac42368063\\ 去 \\
                href = href.replace('\\', '')
                all_video_url.append(PREFIX_BATCH_URL + href)
        all_video_url = list(set(all_video_url))  # 去重

    # 创建目录
    create_directory(f"{VIDEO_DIR}/{name}")

    # 下载
    for item in all_video_url:
        single_download_video(item, name, True)


# 批量下载收藏夹视频，如果第二个参数>0, 则只截取第一页的前slice_count个视频下载
def batch_download_fav_video(batch_url, slice_count=0):
    # 把所有的视频URL放到一个列表中
    all_video_url = []
    # 发请求获取页面数据
    requests_get = requests.get(url=batch_url, headers=headers)
    requests_get.encoding = "utf-8"
    html = requests_get.text
    print(html)
    # 解析数据
    # 先找up主的名字和视频数量以及视频的URL地址
    etree_html = etree.HTML(html)
    # 视频总数量
    num = etree_html.xpath("//li[@class='active']/span/text()")
    num = num[0] if (len(num) > 0) else 0
    # up主的名字
    name = etree_html.xpath("//span[@class='text-overflow name']/text()")
    name = name[0] if (len(name) > 0) else '未定义的up主名称'
    print(f"up主的名字：{name}，视频总数量：{num}")

    # 找到视频的URL地址
    hrefs = etree_html.xpath("//div[@id='ac-space-video-list']/a/@href")
    # 先装第一页的视频URL地址
    all_video_url = [PREFIX_BATCH_URL + href for href in hrefs]
    all_video_url = list(set(all_video_url))  # 去重

    # 截取前slice_count个视频下载
    if slice_count > 0:
        all_video_url = all_video_url[:slice_count]
    else:
        # 找到下一页的url地址，根据num判断页数 一页20个视频
        # 页数
        page = int(num) // 20 + 1
        # 下一页的URL地址
        for i in range(2, page + 1):  # 从第二页开始，因为第一页已经装了
            # 获取当前时间戳
            current_timestamp = time.time()
            next_url = batch_url + f"?quickViewId=ac-space-video-list&reqID={i}&ajaxpipe=1&type=video&order=newest&page={i}&pageSize=20&t={current_timestamp}"
            print(next_url)
            # 发请求获取页面数据
            requests_get = requests.get(url=next_url, headers=headers)
            requests_get.encoding = 'utf-8'
            html = requests_get.text
            # 解析数据 使用正则
            hrefs = re.findall(r'href=\\"(.*?)"', html, re.S)
            for href in hrefs:
                # href /v/ac42368063\\ 去 \\
                href = href.replace('\\', '')
                all_video_url.append(PREFIX_BATCH_URL + href)
        all_video_url = list(set(all_video_url))  # 去重

    # 创建目录
    create_directory(VIDEO_DIR)

    # 下载
    for item in all_video_url:
        single_download_video(item, name, True)


if __name__ == '__main__':
    # test()
    # single_download_video(URL, '测试', False)  # 12.328634262084961 S
    # single_download_video(URL, '', True)  # 8.814500570297241 S
    # batch_download_upper_video(BATCH_URL, 3)
    batch_download_fav_video(BATCH_FAV_URL, 4)
