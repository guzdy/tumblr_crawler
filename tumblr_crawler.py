# !/usr/bin/env python3
# -×- coding: utf-8 -*-

import sys
import configparser
import shlex

from image_downloader import ImagesDownloader
from video_downloader import VideoDownloader


def main(blogname, timesleep=0, proxies=None):
    """ 多线程处理下载图片部分"""
    image = ImagesDownloader()
    video = VideoDownloader()
    image.crawl_image(blogname, proxies=proxies, timeout=TIMEOUT)
    video.crawl_video(blogname, proxies=proxies, timeout=TIMEOUT)


# main 部分， 设置 config 和 命令行参数
if __name__ == "__main__":
    config_parser = configparser.ConfigParser()
    config_parser.read('config.ini')
    BLOGNAME = config_parser.get('USER', 'BLOGNAME')
    blognames = shlex.split(BLOGNAME)
    TIMEOUT = config_parser.getint('USER', 'TIMEOUT')
    TIMESLEEP = config_parser.getint('USER', 'TIMESLEEP')
    try:
        PROXIES = config_parser.get('USER', 'PROXIES')
        if PROXIES:
            PROXIES = eval(PROXIES)
    except:
        PROXIES = None
    print(PROXIES)

    if len(sys.argv) > 1:
        blognames = sys.argv[1:]
    if blognames:
        for blogname in blognames:
            print('尝试下载博客内容，请稍后： %s' % blogname)
            main(blogname, TIMESLEEP, PROXIES)
            print('下载完毕： %s' % blogname)
    else:
        print('请输入正确的博客英文名。')
