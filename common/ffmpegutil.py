import subprocess


def add_cover_to_video(video_path_src, cover_url, video_path_dist):
    ret = -1
    try:
        cmd_str = f'ffmpeg -i {video_path_src} -i {cover_url} -map 0 -map 1 -c copy -c:v:1 png -disposition:v:1 attached_pic {video_path_dist}'
        print('cmd_str-->', cmd_str)
        ret = subprocess.call(cmd_str, shell=True)
        return ret, 'success'
    except Exception as e:
        return ret, e

