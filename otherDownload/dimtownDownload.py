# dimtown.com 下载脚本

import requests  # 发送http请求
import re  # 正则表达式库，用于文本匹配
from lxml import etree  # lxml:解析HTML内容  导入了 lxml 库的 etree 模块
import pprint
import os

from common import logutil
from common import utils


# 单页面下载地址
URL = "https://dimtown.com/115628.html"
# 目标文件目录
TARGET_DIR = 'E:\\video\\dimtown\\2024年8月11日183009'
# 批量下载页面地址
BATCH_URLS = [
    "https://dimtown.com/115628.html"
]

# 请求头，模拟浏览器访问
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 "
                  "Safari/537.36 ",
    # ":authority": '91lt.co'
    # "Cookie": cookie,
    "Referer": "https://dimtown.com/",   # 防盗链
    # "Sec-Ch-Ua": '"Not/A)Brand";v="8", "Chromium";v="126", "Google Chrome";v="126"',
    # "Sec-Ch-Ua-Platform": "Windows"
    # ":path": '/wp-admin/admin-ajax.php?action=search_box',
}

logging = logutil.init_logger('', 'error_log')


# 第一步：解析HTML页面
def get_target_info_and_title(page_url):
    # 1.发送请求获取页面数据
    response = requests.get(page_url, headers=headers)
    if response:
        response.encoding = 'utf-8'
        html = response.text
        # pprint.pprint(f'html:{html}')
        # logging.error(html)
    else:
        pprint.pprint(f'网络请求异常:{page_url}')
        return ''

    # 2.解析数据，先找标题
    # 使用lxml和正则表达式解析HTML
    etree_html = etree.HTML(html)
    # pprint.pprint(f'etree_html: {etree_html}')
    # //div 会选择所有 <div> 元素，而 div 只会选择当前上下文节点的直接子级中的 <div> 元素
    title = etree_html.xpath('//title/text()')
    title = title[0] if (len(title) > 0) else '未定义的title'
    # 去除标题中的特殊字符
    title = utils.file_name_filter(title)
    # pprint.pprint(f'title: {title}')

    # 3.找图片URL
    url_list = etree_html.xpath('//img[@decoding="async"]/@src')
    name_list = etree_html.xpath('//img[@decoding="async"]/@alt')
    filtered_name_list = []
    for name in name_list:
        filtered_name_list.append(utils.file_name_filter(name))
    res_list = list(zip(url_list, name_list))
    # pprint.pprint(res_list)
    return title, res_list


# 批量下载图片
def batch_download(page_urls):
    print(f'批量下载开始，总共{len(page_urls)}个页面')
    succeed = 0
    for index, page_url in enumerate(page_urls):
        print(f'正在下载第{index + 1}个页面')
        download(page_url)
        succeed += 1
    print(f'批量下载完成：({succeed}/{len(page_urls)})')


# 下载图片
def download(page_url):
    title, image_list = get_target_info_and_title(page_url)
    if len(image_list) > 0:
        image_path = os.path.join(TARGET_DIR, title)
        # 确保录存在
        # os.makedirs(os.path.dirname(image_path), exist_ok=True)
        download_images(image_list, image_path)
    else:
        logging.error(f'图片地址获取失败：{title}')
        print(f'图片地址获取失败：{title}')


# 下载图片
def download_images(image_list, image_path):
    folder_name = image_path.split("\\")[-1]
    print(f'图片【{folder_name}】下载中...')
    succeed = 0
    for image in image_list:
        file_name = os.path.join(image_path, f'{image[1]}.jpg')
        ret = do_download_image(image[0], file_name)
        if ret:
            succeed += 1
            print(f'【{image[1]}】下载完成')
    print(f'图片【{folder_name}】下载完毕({succeed}/{len(image_list)})')


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
        print(f'Error downloading image {file_name.split("/")[-1]}: {e}')
        return False


if __name__ == "__main__":
    # get_target_info_and_title()
    # download(URL)
    batch_download(BATCH_URLS)
