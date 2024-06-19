# 说明

该项目分为三个模块：下载A站视频、下载B站视频以及对于缓存的B站视频，批量合并vieo.m4s和audio.m4s为MP4文件。

## 一、下载A站视频

`aFunDownload`模块：支持批量下载某个up主的所有视频，也支持批量下载收藏夹中的视频（需要替换自己的`Cookie`）。对于下载的视频支持添加网络封面图，如果获取失败，则会从下载的视频中选取一帧图像作为封面图。

## 二、下载B站视频

`bilibiliDownload`模块：目前仅支持下载单个视频，集下载和音视频合并功能于一身。

## 三、B站缓存视频合并

`bilibiliConverter`模块：将缓存的B站视频（`video.m4s`,`audio.m4s`）批量转换为MP4格式，支持普通视频和番剧。

```python
# 普通视频合并
convert_normal_video()
# 番剧视频合并
convert_anime_video()
```