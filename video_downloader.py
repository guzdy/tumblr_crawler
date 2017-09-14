# !/usr/bin/env python3
# -×- coding: utf-8 -*-

import asyncio
from concurrent import futures
import json
import requests
import os
import multiprocessing
import re
import datetime

from image_downloader import TextWriter

from requests.packages.urllib3.exceptions import InsecureRequestWarning
# 禁用安全请求警告
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)



HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36",
    "Upgrade-Insecure-Requests": "1"
    }
PROCESSES = multiprocessing.cpu_count()


class VideoDownloader(object):

    def crawl_video(self, blogname, proxies=None, timeout=None):
        """该 class 的控制模块, num 为 posts 总数， start 为起始数"""
        num = 1
        start = 0
        text = TextWriter(blogname)
        with futures.ProcessPoolExecutor(max_workers=PROCESSES * 2) as ex:
            while num > start:
                data_json = self.page_download(blogname, start, proxies, timeout)
                item_list, num = self.page_parse(data_json)
                start += 50
                for item in item_list:
                    ex.submit(self.media_download, item['media'], item['slug'],
                              blogname, proxies=proxies, timeout=timeout)
                    text.process_item(item)
        text.close()

    def page_download(self, blogname, start, proxies=None, timeout=None, retry_times=0):
        url_raw = "http://{0}.tumblr.com/api/read/json?type=video&num=50&start={1}"
        url = url_raw.format(blogname, start)
        print('尝试下载: ', url)
        resp = requests.get(url, proxies=proxies, headers=HEADERS, verify=False)
        if resp.status_code != 200:
            if retry_times > 3:
                print('多次尝试下载后失败，结束图片页面下载')
                return
            retry_times += 1
            return self.page_download(self, blogname, proxies, timeout, retry_times)
        data_json = json.loads(resp.text.strip('var tumblr_api_read = ').strip(';\n'))
        return data_json

    def page_parse(self, data):
        item_list =[]
        for post in data['posts']:
            item ={}
            video_html = post['video-player']
            pattern_hd = re.compile(r'"hdUrl":(?:"(\S+?)"|false),')
            video_url = pattern_hd.findall(video_html)[0].replace('\\', '')
            if not video_url:
                pattern_normal = re.compile(r'<source src="(\S+?)"')
                video_url = pattern_normal.findall(video_html)[0]
            item['media'] = video_url
            slug = post['slug']
            item['slug'] = slug
            item_list.append(item)
        num = data['posts-total']
        return item_list, num

    def media_download(self, url, filename, blogname, proxies=None, timeout=None):
        event_loop = asyncio.new_event_loop()
        event_loop.run_until_complete(self.async_download(url, filename, blogname,
                                                          proxies, timeout))
        event_loop.close()
        return

    async def async_download(self, url, filename_raw, blogname, proxies, timeout):
        """ 指定下载路径， 并下载图片。 """
        print('File name RAW:', filename_raw)
        if not os.path.isdir(blogname):
            os.mkdir(blogname)
        num = 1
        if not filename_raw:
            print("Video Url:", url)
            filename = url.split('/')[-1] + '.mp4'
        else:
            if num == 1:
                filename = filename_raw + '.mp4'
            else:
                filename = "{0}({1}).mp4".format(filename_raw, str(num))
            num += 1
        file_path = os.path.join(blogname, filename)
        print("Video File Path: ", file_path)
        if not os.path.isfile(file_path):
            await self._async_download(url, file_path, proxies, timeout)

    async def _async_download(self, url, file_path, proxies, timeout, retry_times=0):
        """ 下载图片， 出现错误，最多重试三次， . """
        try:
            resp = requests.get(url, proxies=proxies, stream=True,
                                timeout=timeout, headers=HEADERS, verify=False)
            if resp.status_code != 200:
                raise Exception('尝试下载影像时，出现错误，重试' % resp.status_code)
            with open(file_path, 'wb') as f:
                for chunk in resp.iter_content(1024 * 100):
                    f.write(chunk)
        except Exception as e:
            print("%s: %s" % (e, url))
            # try again
            if retry_times < 3:
                retry_times += 1
                # 如需设置proxies, 在下行代码设置设置
                await self._async_download(url, file_path, proxies, timeout, retry_times)
            else:
                print("Download Fail(retried 3 times)： ", url)
        return


class TextWriter(object):
    """把必要的内容文本写入保存"""

    def __init__(self, blogname):
        if not os.path.isdir(blogname):
            os.mkdir(blogname)
        strtime = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        file_path = os.path.join(blogname, '0.'+blogname+' video '+strtime+'.txt')
        self.file = open(file_path, 'w')

    def close(self):
        self.file.close()

    def process_item(self, item):
        if item.get("media"):
            line = item['media'] + '\n'
            self.file.write(line)

        if item.get('tags'):
            self.file.write('Tags:')
            for tag in item['tags']:
                self.file.write(tag)
            self.file.write('\n')

        if item.get('slug'):
            text = re.sub(r'\xa0|\n', ' ', item['slug'].strip())
            text = re.sub(r'\s+', ' ', text)
            self.file.write(text+'\n')
        self.file.write('\n\n')

        return
