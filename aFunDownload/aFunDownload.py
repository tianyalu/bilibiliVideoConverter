"""
正常的视频：
    完整的视频数据 --> 直接下载
流媒体：
    视频数据 --> 分段 --> 每一段视频数据的url地址 --> 下载
    把完整的视频分成很多小段，每一段视频数据的url地址 ts文件
1. 通过分析网页源代码，找到视频的url地址
2. 通过requests模块发送请求，获取响应数据

3. 保存视频数据
4. 给视频加封面：ffmpeg -i output.mp4 -i cover.jpeg -map 0 -map 1 -c copy -c:v:1 png -disposition:v:1 attached_pic output_with_cover.mp4

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
import subprocess
import os
import pprint
import time
from common import logutil
from common import fileutil
from common import jsonutil


# 1.确定url地址

# 单视频下载
# URL = "https://www.acfun.cn/v/ac43577708"
# URL = "https://m.acfun.cn/v/?ac=44523314&sid=d75e7106fb456c95"
# URL = "https://m.acfun.cn/v/?ac=44523314"
# URL = "https://www.acfun.cn/v/ac35582241"
# URL = "https://www.acfun.cn/v/ac35437039"
# URL = "https://www.acfun.cn/v/ac44546118"
URL = "https://www.acfun.cn/v/ac44581895"
# URL = 'https://www.acfun.cn/u/56776847?quickViewId=ac-space-video-list&reqID=2&ajaxpipe=1&type=video&order=newest&page=1&pageSize=20&t=1705985425289'
# 视频前缀
PREFIX_URL = "https://ali-safety-video.acfun.cn/mediacloud/acfun/acfun_video"

# 批量下载（下载一个up主的所有视频）
# 批量下载的URL
BATCH_URL = "https://www.acfun.cn/u/56776847"
BATCH_FAV_URL = "https://www.acfun.cn/member/favourite/folder/74465596"
# 视频前缀
PREFIX_BATCH_URL = "https://www.acfun.cn"

# VIDEO_DIR = 'file/video'
VIDEO_DIR = 'E:/Video/Afun/k_2024年5月20日005857'
PAGE_SIZE_UPPER = 20
PAGE_SIZE_FAV = 30

logging = logutil.init_logger('', 'error_log')

cookie = '_did=web_1919071475B7ED70; _did=web_1919071475B7ED70; lsv_js_player_v2_main=e4d400; acPasstoken=ChVpbmZyYS5hY2Z1bi5wYXNzdG9rZW4ScF2AZBASWJBFsWB0xB39NEqKKelTamMDfm8scx1mth7iVfK8w74NlNLBA1QLQYQENIbtkrsTPGmyPWZkOneQKIOCePekEYm_3adZb5xTPiLgoXNKuVUxpYhgwiazGRXudj8VWgPlZY--4kEL1wsxV9waEpeyvoxdTP1KmaSqp4F28QDqNSIgbVND-loy2pzkwFGTBTFU_jYdl6IB5psALRWxpIi2M7EoBTAB; auth_key=19410036; ac_username=%E5%A4%A9%E6%B6%AF%E8%B7%AF2; acPostHint=5b56db99e87800bdb756f41e3b687e1123e6; ac_userimg=https%3A%2F%2Fimgs.aixifan.com%2Fstyle%2Fimage%2F201908%2FGEf9kCBCmahRBHsZJc5clycPZnjUSMRe.jpg; csrfToken=xawyH1WsrXzT92ngO2De-QGA; webp_supported=%7B%22lossy%22%3Atrue%2C%22lossless%22%3Atrue%2C%22alpha%22%3Atrue%2C%22animation%22%3Atrue%7D; Hm_lvt_2af69bc2b378fb58ae04ed2a04257ed1=1715875645,1715963538,1716043889,1716136141; safety_id=AAI3eYMjDISBr2-FAIkGDXAu; Hm_lpvt_2af69bc2b378fb58ae04ed2a04257ed1=1716136263; cur_req_id=5453027953911712_self_c229e41ea74e92504879af6cbf55b116; cur_group_id=5453027953911712_self_c229e41ea74e92504879af6cbf55b116_0'
# 请求头，模拟浏览器访问
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 "
                  "Safari/537.36 ",
    "Cookie": cookie
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
    title = re.sub(r"[\/\\\:\*\?\"\<\>\|\s]", "", title)  # 清理标题中的特殊字符
    # 再找视频的URL地址
    # re.S：标志参数，表示在匹配时考虑换行符。因为正则表达式中的 . 默认不匹配换行符
    videoInfo = re.findall(r"window.pageInfo = window.videoInfo = (.*?);", html, re.S)
    videoInfo = videoInfo[0] if (len(videoInfo) > 0) else '未定义的videoInfo'
    if not jsonutil.is_valid_json(videoInfo):
        print('JSON 非法')
        videoInfo = get_video_info_again(html)
    print(videoInfo)

    # logging.error('alkfdjadsl')
    # logging.error(videoInfo)
    return videoInfo, title


def get_video_info_again(text):
    # 定义正则表达式模式
    pattern = r'window\.pageInfo\s*=\s*window\.videoInfo\s*=\s*({.*?};)'
    # 使用 re.findall() 提取匹配的内容
    matches = re.findall(pattern, text)
    # print(matches)
    matches = matches[0] if (len(matches) > 0) else '未定义的videoInfo'
    if matches.endswith(';'):
        matches = matches[:-1]
    return matches


# 第二步：解析视频数据
def parse_data(videoInfo):
    # 解析JSON数据
    ksPlayJson = json.loads(videoInfo)['currentVideoInfo']['ksPlayJson']
    print(ksPlayJson)
    representation = json.loads(ksPlayJson)['adaptationSet'][0]['representation']
    backupUrl = representation[0]['backupUrl'][0]  # 视频的URL地址

    cover_img_info = json.loads(videoInfo)['coverImgInfo']
    cover_image_url = cover_img_info['thumbnailImage']['cdnUrls'][0]['url']
    print(f'cover_image_url--> {cover_image_url}')

    # 请求视频数据
    m3u8_data = requests.get(url=backupUrl, headers=headers)
    m3u8_data.encoding = 'utf-8'
    # print(m3u8_data.text)
    # 使用正则表达式找到所有的视频片段URL
    segments = re.findall(r",\n(.*?)\n#E", m3u8_data.text, re.S)
    return segments, cover_image_url


# 第三步：下载视频片段
def download_segment(args):
    # 下载单个视频片段
    index, segment_url, title = args
    segment_url = segment_url if (segment_url.startswith('http')) else f'{PREFIX_URL}/{segment_url}'
    temp_filename = f"{VIDEO_DIR}/temp_{index:05d}.ts"
    try:
        # print(f'\nsegment url --> {segment_url}')
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
        print(f"视频合并完成({len(segment_files)}/{len(segments)})：{final_name}")
        print(f"用时：{end_time - start_time} S")
    else:
        print("某些片段下载失败，视频可能不完整")


# 下载视频
def download_video(segments, final_name):
    start_time = time.time()
    total_segment = 0
    title = final_name.split('/')[-1]
    for item in tqdm(segments):
        # 拼接视频的URL地址
        m3u8_download_url = f'{PREFIX_URL}/{item}'
        # print(m3u8_download_url)
        # 下载视频数据
        video_get = requests.get(url=m3u8_download_url, headers=headers)
        if video_get.status_code != 200:
            pprint.pprint(f"{title} 下载失败，丢失片段{m3u8_download_url}，状态码：{video_get.status_code}")
            continue
        else:
            total_segment += 1
            video = video_get.content
            with open(final_name, 'ab') as f:  # append binary
                f.write(video)
                f.close()
    end_time = time.time()
    print(f"下载完成 {title} \n完成率：{total_segment}/{len(segments)}")
    print(f'用时：{end_time - start_time} S')


def get_file_name(title):
    fileutil.create_directory(VIDEO_DIR)
    final_name = f"{VIDEO_DIR}/{title}.mp4"
    return final_name


def merge_video_cover_img(video_path, cover_url):
    title = video_path.split('/')[-1]
    ori_path = video_path.split('.')[0]
    temp_name = f'{ori_path}___without_cover.mp4'
    # 原文件先重命名为临时文件
    os.rename(video_path, temp_name)

    # 视频添加封面图
    ret = -1
    try:
        cmd_str = f'ffmpeg -i {temp_name} -i {cover_url} -map 0 -map 1 -c copy -c:v:1 png -disposition:v:1 attached_pic {video_path}'
        print('cmd_str-->', cmd_str)
        ret = subprocess.call(cmd_str, shell=True)
        print(f'{title} execute cmd result -> {ret}')
    except Exception as e:
        logging.error(f'{title} 添加封面图时出错：{str(e)}')
        print(f'{title} 添加封面图时出错 -> ', e)
    # 删除临时文件
    if ret == 0:
        os.remove(temp_name)


def single_download_video(url, isConcurrently=True):
    videoInfo, title = get_video_info_and_title(url)
    findall, cover_image_url = parse_data(videoInfo)
    final_name = get_file_name(title)
    print(f'final_name --> {final_name}')
    # return
    # 下载视频
    if isConcurrently:
        download_video_concurrently(findall, final_name)
    else:
        download_video(findall, final_name)
    # 添加视频封面
    merge_video_cover_img(final_name, cover_image_url)


# 批量下载up主的视频，如果第二个参数>0, 则只截取前slice_count个视频下载
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
    if slice_count > 0 and len(all_video_url) <= PAGE_SIZE_UPPER:
        all_video_url = all_video_url[:slice_count]
    else:
        # 找到下一页的url地址，根据num判断页数 一页20个视频
        # 页数
        page = int(num) // PAGE_SIZE_UPPER + 1
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
        if slice_count > 0:
            all_video_url = all_video_url[:slice_count]
        # all_video_url = list(set(all_video_url))  # 去重

    # 下载
    for item in all_video_url:
        single_download_video(item, True)


# 批量下载收藏夹视频，如果第二个参数>0, 则只截取前slice_count个视频下载
def batch_download_fav_video(batch_url, slice_count=0):
    # 把所有的视频URL放到一个列表中
    all_video_url = []
    # 发请求获取页面数据
    requests_get = requests.get(url=batch_url, headers=headers)
    requests_get.encoding = "utf-8"
    html = requests_get.text
    # print(html)
    # logging.error(html)
    # return
    # 解析数据
    # 先找up主的名字和视频数量以及视频的URL地址
    etree_html = etree.HTML(html)
    # 视频总数量
    # num = etree_html.xpath("//li[@class='active']/span/text()")
    # num = num[0] if (len(num) > 0) else 0
    # print(f"视频总数量：{num}")

    # 找到视频的URL地址
    hrefs = etree_html.xpath("//div[@class='ac-member-favourite-douga-item-cover ']/a/@href")
    # print(hrefs)
    # 先装第一页的视频URL地址
    all_video_url = [PREFIX_BATCH_URL + href for href in hrefs]
    # all_video_url = list(set(all_video_url))  # 去重
    print(f'all_video_url[{len(all_video_url)}]--> {all_video_url}')

    # 截取前slice_count个视频下载
    if slice_count > 0 and len(all_video_url) <= PAGE_SIZE_FAV:
        all_video_url = all_video_url[:slice_count]
    else:
        print('else branch todo')
        # 找到下一页的url地址，根据num判断页数 一页30个视频
        # 页数
        # page = int(num) // PAGE_SIZE_FAV + 1
        # # 下一页的URL地址
        # for i in range(2, page + 1):  # 从第二页开始，因为第一页已经装了
        #     # 获取当前时间戳
        #     current_timestamp = time.time()
        #     next_url = batch_url + f"?quickViewId=ac-space-video-list&reqID={i}&ajaxpipe=1&type=video&order=newest&page={i}&pageSize=20&t={current_timestamp}"
        #     print(next_url)
        #     # 发请求获取页面数据
        #     requests_get = requests.get(url=next_url, headers=headers)
        #     requests_get.encoding = 'utf-8'
        #     html = requests_get.text
        #     # 解析数据 使用正则
        #     hrefs = re.findall(r'href=\\"(.*?)"', html, re.S)
        #     for href in hrefs:
        #         # href /v/ac42368063\\ 去 \\
        #         href = href.replace('\\', '')
        #         all_video_url.append(PREFIX_BATCH_URL + href)
        # all_video_url = list(set(all_video_url))  # 去重


    # 下载
    for item in all_video_url:
        single_download_video(item, True)


if __name__ == '__main__':
    # single_download_video(URL, False)  # 12.328634262084961 S
    single_download_video(URL, True)  # 8.814500570297241 S
    # batch_download_upper_video(BATCH_URL, 3)
    # batch_download_fav_video(BATCH_FAV_URL, 2)
