# 51下载器

import binascii
import random
import requests
import re
from lxml import etree
import json
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed
import os
import m3u8
import time
from datetime import datetime
import sys

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from common import logutil

# pip install pycryptodome
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

VIDEO_DIR = 'G:\\video\\YouTube\\51\\2024年8月17日213855'
KEY_FILE = f'{VIDEO_DIR}/video.key'  # m3u8的秘钥文件
key = None
key_iv = None

# 直接在代码中定义要下载的URL列表
DOWNLOAD_URLS = [
    # "https://bridge.pyngdvop.cc/archives/216686/",
    # "https://bridge.pyngdvop.cc/archives/216687/",
    # "https://bridge.pyngdvop.cc/archives/216688/",
    # 可以继续添加更多URL
    "https://actor.ojounxvc.cc/archives/222403/",
]

# 下载配置
OVERWRITE_FILES = True  # 是否覆盖已存在的文件
DOWNLOAD_DELAY = 3      # 下载间隔时间（秒）

logging = logutil.init_logger('', 'error_log')

# 请求头，模拟浏览器访问
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 "
                  "Safari/537.36 ",
}


# 第一步：分析视频页面
def get_video_info_and_title(url):
    """获取视频信息和标题"""
    response = requests.get(url=url, headers=headers)
    if response:
        response.encoding = "utf-8"
        html = response.text
        logging.error(html)

    # 解析数据，先找标题
    # 解析HTML内容，构建XPath查询对象
    etree_html = etree.HTML(html)
    # 提取<title>标签的文本作为视频标题
    title = etree_html.xpath('//title/text()')
    title = title[0] if (len(title) > 0) else '未定义的title'
    # 去除标题中的特殊字符
    title = re.sub(r"[\/\\\:\*\?\"\<\>\|\s]", "", title)
    delimiter = '91分享'
    if delimiter in title:
        title = title.split(delimiter)[0]

    # 再找视频的URL地址
    video_urls = etree_html.xpath('//div/@video-url')
    if len(video_urls) == 0:
        print(f'视频地址获取失败：{title}')

    # 查找M3U8 URL模式
    m3u8_patterns = [
        r'"(https?://[^"]*\.m3u8[^"]*)"',
        r'"(https?://[^"]*m3u8[^"]*)"',
        r'm3u8[_-]?url["\']?\s*[:=]\s*["\']?(https?://[^"\']+)',
        r'video[_-]?url["\']?\s*[:=]\s*["\']?(https?://[^"\']*m3u8[^"\']*)',
        r'src["\']?\s*[:=]\s*["\']?(https?://[^"\']*\.m3u8[^"\']*)'
    ]
    
    # 如果没找到video-url属性，尝试从HTML中查找M3U8 URL
    if len(video_urls) == 0:
        for pattern in m3u8_patterns:
            matches = re.findall(pattern, html)
            for match in matches:
                if match and match not in video_urls:
                    video_urls.append(match)
                    print(f'找到M3U8 URL: {match}')

    # 找图片urls
    image_urls = etree_html.xpath('//figure[@class="wp-block-image"]//img/@data-src')
    if len(image_urls) == 0:
        print(f'未获取到图片url')

    return video_urls, image_urls, title


def download(page_url, overwrite=False):
    """下载视频和图片"""
    video_urls, image_urls, title = get_video_info_and_title(page_url)
    print(f'video_urls: {video_urls}')
    print(f'image_urls: {image_urls}')
    print(f'title: {title}')
    return
    if len(image_urls) > 0 or len(video_urls) > 0:
        video_path = os.path.join(VIDEO_DIR, title)
        
        # 检查是否已存在文件
        if not overwrite:
            existing_files = check_existing_files(video_path, title, len(video_urls))
            if existing_files:
                print(f"⚠️ 文件已存在，跳过下载: {title}")
                print(f"   如需覆盖，请设置 overwrite=True")
                return False
        
        # 确保目录存在
        os.makedirs(video_path, exist_ok=True)
        
        if len(image_urls) > 0:
            image_path = os.path.join(video_path, 'pic')
            download_images(image_urls, image_path, overwrite)
        else:
            logging.error(f'图片地址获取失败：{title}')
            print(f'图片地址获取失败：{title}')

        if len(video_urls) > 0:
            download_video(video_urls, video_path, title, overwrite)
        else:
            logging.error(f'视频地址获取失败：{title}')
            print(f'视频地址获取失败：{title}')
    else:
        logging.error(f'视频图片地址均获取失败：{title}')
        print(f'视频图片地址均获取失败：{title}')
    
    return True


def check_existing_files(video_path, title, video_count):
    """检查文件是否已存在"""
    if not os.path.exists(video_path):
        return False
    
    # 检查视频文件
    if video_count == 1:
        video_file = os.path.join(video_path, f'{title}.mp4')
        if os.path.exists(video_file):
            return True
    else:
        # 检查多个视频文件
        for index in range(video_count):
            video_file = os.path.join(video_path, f'{title}{index}.mp4')
            if os.path.exists(video_file):
                return True
    
    # 检查图片目录
    image_path = os.path.join(video_path, 'pic')
    if os.path.exists(image_path):
        image_files = [f for f in os.listdir(image_path) if f.endswith('.jpg')]
        if len(image_files) > 0:
            return True
    
    return False


def get_unique_filename(base_path, filename):
    """获取唯一的文件名，如果文件存在则添加随机数后缀"""
    if not os.path.exists(os.path.join(base_path, filename)):
        return filename
        
    # 分离文件名和扩展名
    name, ext = os.path.splitext(filename)
    
    # 生成带随机数的新文件名
    while True:
        random_suffix = random.randint(1000, 9999)
        new_filename = f"{name}_{random_suffix}{ext}"
        if not os.path.exists(os.path.join(base_path, new_filename)):
            print(f"📝 文件已存在，重命名为: {new_filename}")
            return new_filename


def download_images(image_urls, image_path, overwrite=False):
    """下载图片"""
    print(f'图片下载中...')
    succeed = 0
    
    for url in image_urls:
        original_filename = f'{url.split("/")[-1]}.jpg'
        
        # 检查文件是否已存在并处理重命名
        if not overwrite:
            original_filename = get_unique_filename(image_path, original_filename)
        
        file_name = os.path.join(image_path, original_filename)
        ret = do_download_image(url, file_name)
        if ret:
            succeed += 1
    print(f'图片下载完毕({succeed}/{len(image_urls)})')


def do_download_image(url, file_name):
    """真正下载图片"""
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        # 确保目录存在
        os.makedirs(os.path.dirname(file_name), exist_ok=True)
        # 将图片写入文件
        with open(file_name, 'wb') as file:
            file.write(response.content)
            return True
    except requests.RequestException as e:
        print(f'Error downloading image {file_name.split("./")[-1]}: {e}')
        return False


def download_video(video_urls, video_path, title, overwrite=False):
    """下载视频"""
    print(f'视频【{title}】下载中...')
    
    # 下载视频
    if len(video_urls) == 1:
        video_name = f'{title}.mp4'
        
        # 检查文件是否已存在并处理重命名
        if not overwrite:
            video_name = get_unique_filename(video_path, video_name)
        
        output_file = os.path.join(video_path, video_name)
        do_download(video_urls[0], output_file)
        
    elif len(video_urls) > 1:
        for index, video_url in enumerate(video_urls, start=0):
            video_name = f'{title}{index}.mp4'
            
            # 检查文件是否已存在并处理重命名
            if not overwrite:
                video_name = get_unique_filename(video_path, video_name)
            
            output_file = os.path.join(video_path, video_name)
            do_download(video_urls[index], output_file)


def do_download(url, output_file):
    """执行下载"""
    clean_url = url.strip()
    if clean_url.endswith('m3u8'):
        download_m3u8(clean_url, output_file)


def download_m3u8(m3u8_url, output_file):
    """下载m3u8视频"""
    # 确保输出目录存在
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    print(f"🎬 开始下载M3U8视频: {m3u8_url}")
    
    # 验证URL格式
    if '.m3u8' not in m3u8_url:
        raise ValueError(f"❌ 无效的M3U8 URL: {m3u8_url} (应该包含.m3u8)")
    
    # 下载 m3u8 文件
    try:
        print("📥 正在加载M3U8播放列表...")
        m3u8_obj = m3u8.load(m3u8_url)
        
        if not m3u8_obj.segments:
            raise ValueError("❌ M3U8播放列表为空，没有找到视频片段")
            
        segments = m3u8_obj.segments
        segment_urls = [segment.absolute_uri for segment in segments]
        
        print(f"📊 找到 {len(segment_urls)} 个视频片段")
        
        # 获取秘钥信息
        if m3u8_obj.keys:
            key_info = m3u8_obj.keys[0]
            global key, key_iv
            key_url = key_info.absolute_uri
            print(f"🔑 发现加密密钥: {key_url}")
            
            # 处理IV值
            if key_info.iv:
                if key_info.iv.startswith('0x'):
                    key_iv = binascii.unhexlify(key_info.iv[2:])
                else:
                    key_iv = binascii.unhexlify(key_info.iv)
            else:
                key_iv = None
                
            # 下载密钥文件
            print("🔐 正在下载密钥文件...")
            download_key(key_url, KEY_FILE)
            with open(KEY_FILE, 'rb') as f:
                key = f.read()
            print(f"✅ 密钥下载完成，长度: {len(key)} 字节")
        else:
            print("ℹ️ 未发现加密，使用明文下载")
            key = None
            key_iv = None

        # 执行下载操作
        print("🚀 开始下载视频片段...")
        download_video_concurrently(segment_urls, output_file)
        
    except requests.RequestException as e:
        print(f"❌ 网络请求失败: {e}")
        raise
    except Exception as e:
        if "InvalidPlaylist" in str(type(e)):
            print(f"❌ M3U8播放列表格式错误: {e}")
        elif "HTTP" in str(e) or "404" in str(e) or "403" in str(e):
            print(f"❌ 网络请求失败: {e}")
        else:
            print(f"❌ M3U8下载失败: {e}")
        logging.error(f'M3U8下载失败: {m3u8_url} - {e}')
        raise


def download_key(url, dest):
    """下载秘钥文件"""
    response = requests.get(url)
    response.raise_for_status()
    with open(dest, 'wb') as f:
        f.write(response.content)
    return dest


def download_segment(args):
    """下载视频片段"""
    index, segment_url, title = args
    seg_url = segment_url if (segment_url.startswith('http')) else segment_url
    temp_filename = f"{VIDEO_DIR}/temp_{index:05d}.ts"
    ret = do_download_segment(index, seg_url, temp_filename)
    if ret:
        return index, temp_filename
    else:
        return index, None


def do_download_segment(index, segment_url, temp_filename):
    """真正下载片段"""
    try:
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


def decrypt_file(input_file, output_file):
    """解密文件"""
    try:
        if key is None:
            # 如果没有密钥，直接复制文件
            with open(input_file, 'rb') as f_in:
                with open(output_file, 'wb') as f_out:
                    f_out.write(f_in.read())
            return
            
        # 使用AES解密
        if key_iv is not None:
            cipher = AES.new(key, AES.MODE_CBC, key_iv)
        else:
            cipher = AES.new(key, AES.MODE_CBC)
            
        with open(input_file, 'rb') as f:
            ciphertext = f.read()
            
        # 解密并去除填充
        plaintext = unpad(cipher.decrypt(ciphertext), AES.block_size)
        
        with open(output_file, 'wb') as f:
            f.write(plaintext)
            
    except Exception as e:
        print(f"❌ 解密失败 {input_file}: {e}")
        # 如果解密失败，尝试直接复制
        try:
            with open(input_file, 'rb') as f_in:
                with open(output_file, 'wb') as f_out:
                    f_out.write(f_in.read())
        except Exception as e2:
            print(f"❌ 文件复制也失败: {e2}")
            raise


def merge_video_segments(segment_files, final_path):
    """合并所有视频片段"""
    print(f"🔧 开始合并 {len(segment_files)} 个视频片段...")
    
    with open(final_path, 'wb') as final_file:
        for i, segment_file in enumerate(segment_files):
            if segment_file is None:
                print(f"⚠️ 跳过空片段 {i}")
                continue
                
            decrypted_file = f'{segment_file}_decrypted'
            try:
                # 解密文件
                decrypt_file(segment_file, decrypted_file)
                
                # 读取解密后的内容并写入最终文件
                with open(decrypted_file, 'rb') as f:
                    content = f.read()
                    final_file.write(content)
                    print(f"✅ 合并片段 {i+1}/{len(segment_files)}: {len(content)} 字节")
                
                # 清理临时文件
                if os.path.exists(segment_file):
                    os.remove(segment_file)
                if os.path.exists(decrypted_file):
                    os.remove(decrypted_file)
                    
            except Exception as e:
                print(f"❌ 合并片段 {i+1} 失败: {e}")
                continue
    
    # 清理密钥文件
    if os.path.exists(KEY_FILE):
        os.remove(KEY_FILE)
        
    print(f"🎉 视频合并完成: {final_path}")


def download_video_concurrently(segments, final_name):
    """并发下载视频片段"""
    start_time = time.time()
    title = final_name.split('/')[-1]
    segment_urls = [segment_url for segment_url in segments]
    # 准备下载任务
    tasks = [(index, segment_url, title) for index, segment_url in enumerate(segment_urls)]
    # 存储临时文件名
    segment_files = [None] * len(segments)
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


def batch_download(urls, overwrite=False, delay=2):
    """批量下载视频"""
    print(f"🎯 批量下载 {len(urls)} 个视频")
    print(f"📁 下载目录: {VIDEO_DIR}")
    print(f"🔄 覆盖模式: {'开启' if overwrite else '关闭'}")
    print(f"⏱️ 下载间隔: {delay} 秒")
    print("=" * 50)
    
    success_count = 0
    for i, url in enumerate(urls, 1):
        print(f"\n📥 开始下载 [{i}/{len(urls)}]: {url}")
        try:
            if download(url, overwrite):
                success_count += 1
                print(f"✅ 下载成功 [{i}/{len(urls)}]")
            else:
                print(f"⚠️ 下载跳过 [{i}/{len(urls)}]")
        except Exception as e:
            print(f"❌ 下载失败 [{i}/{len(urls)}]: {e}")
            logging.error(f'批量下载失败 [{i}/{len(urls)}]: {url} - {e}')
        
        # 添加延迟避免请求过快
        if i < len(urls):
            print(f"⏳ 等待 {delay} 秒...")
            time.sleep(delay)
    
    print(f"\n🎉 批量下载完成: {success_count}/{len(urls)} 个视频成功")


def download_from_urls_list(urls=None, overwrite=None, delay=None):
    """
    从代码中定义的URL列表批量下载视频
    
    Args:
        urls: URL列表，默认为DOWNLOAD_URLS
        overwrite: 是否覆盖已存在的文件，默认为OVERWRITE_FILES
        delay: 下载间隔时间（秒），默认为DOWNLOAD_DELAY
    """
    # 使用默认值
    if urls is None:
        urls = DOWNLOAD_URLS
    if overwrite is None:
        overwrite = OVERWRITE_FILES
    if delay is None:
        delay = DOWNLOAD_DELAY
    
    print("🎯 51视频下载器")
    print(f"📁 下载目录: {VIDEO_DIR}")
    print("=" * 50)
    
    if not urls:
        print(f"❌ 没有找到有效的URL")
        return False
    
    # 开始批量下载
    batch_download(urls, overwrite, delay)
    return True


def test_m3u8_download():
    """测试M3U8下载功能"""
    # 正确的M3U8播放列表URL（不是密钥文件）
    # test_m3u8_url = "https://hls.liheiat.xyz/videos5/9134db8c5b32ceb8a5707b9cae6cebb7/9134db8c5b32ceb8a5707b9cae6cebb7.m3u8?auth_key=1757937959-68c801279b6fb-0-b63fcae38f253e252e395d23fb8f2274&v=3&time=0"
    test_m3u8_url = "https://hls.usoryy.cn/videos5/9134db8c5b32ceb8a5707b9cae6cebb7/9134db8c5b32ceb8a5707b9cae6cebb7.m3u8?auth_key=1758802273-68d53161f2e8a-0-be87831c27398271656f94e44f07cbfd&v=3&time=0"
    test_output = os.path.join(VIDEO_DIR, "test_m3u8_video.mp4")
    
    print("🧪 测试M3U8下载功能")
    print(f"📥 测试URL: {test_m3u8_url}")
    print(f"📁 输出文件: {test_output}")
    print("=" * 50)
    
    # 验证URL是否为M3U8文件
    if '.m3u8' not in test_m3u8_url:
        print("❌ 错误：提供的URL不是M3U8播放列表文件")
        print("💡 提示：M3U8文件应该包含.m3u8")
        return
    
    try:
        download_m3u8(test_m3u8_url, test_output)
        print("✅ M3U8下载测试成功！")
    except Exception as e:
        print(f"❌ M3U8下载测试失败: {e}")
        print("💡 可能的原因：")
        print("   1. URL已过期（auth_key有时间限制）")
        print("   2. 网络连接问题")
        print("   3. 服务器拒绝访问")


if __name__ == '__main__':
    # 测试M3U8下载功能
    # test_m3u8_download()
    
    # 使用代码中定义的URL列表和配置进行下载
    download_from_urls_list()
    
    # 或者自定义URL列表和配置
    # custom_urls = [
    #     "https://bridge.pyngdvop.cc/archives/216686/",
    #     "https://bridge.pyngdvop.cc/archives/216687/",
    # ]
    # download_from_urls_list(urls=custom_urls, overwrite=True, delay=5)

