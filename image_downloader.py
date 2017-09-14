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
from requests.packages.urllib3.exceptions import InsecureRequestWarning
# 禁用安全请求警告
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36",
    "Upgrade-Insecure-Requests": "1"
    }
PROCESSES = multiprocessing.cpu_count()


class ImagesDownloader(object):

    def crawl_image(self, blogname, proxies=None, timeout=None):
        """该 class 的控制模块, num 为 posts 总数， start 为起始数"""
        num = 1
        start = 0
        text = TextWriter(blogname)
        with futures.ProcessPoolExecutor(max_workers=PROCESSES) as ex:
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
        url_raw = "http://{0}.tumblr.com/api/read/json?type=photo&num=50&start={1}"
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
        num = data['posts-total']
        if num == 0:
            return

        item_list = []
        for post in data['posts']:
            item = {}
            print(post)
            if post.get('photos'):
                photos = []
                for photo in post["photos"]:
                    photos.append(photo['photo-url-1280'])
            else:
                photos = [post['photo-url-1280']]
            item['media'] = photos
            slug = post.get('slug')
            item['slug'] = slug
            tags_list = post.get('tags')
            item['tags_list'] = tags_list
            item_list.append(item)
            print("ITEM INFO:", item_list)
        return item_list, num

    def media_download(self, urls, filename, blogname, proxies=None, timeout=None):
        event_loop = asyncio.new_event_loop()
        event_loop.run_until_complete(self.async_download(urls, filename, blogname,
                                                          proxies, timeout))
        event_loop.close()
        return

    async def async_download(self, urls, filename_raw, blogname, proxies, timeout):
        """ 指定下载路径， 并下载图片。 """
        print('File name RAW:', filename_raw)
        if not os.path.isdir(blogname):
            os.mkdir(blogname)
        num = 1
        for url in urls:
            if not filename_raw:
                print("Image Url:", url)
                filename = url.split('/')[-1]
            else:
                if num == 1:
                    filename = filename_raw + '.jpg'
                else:
                    filename = "{0}({1}).jpg".format(filename_raw, str(num))
                num += 1
            file_path = os.path.join(blogname, filename)
            print("Image File Path: ", file_path)
            if not os.path.isfile(file_path):
                await self._async_download(url, file_path, proxies, timeout)

    async def _async_download(self, url, file_path, proxies, timeout, retry_times=0):
        """ 下载图片， 出现错误，最多重试三次， . """
        try:
            resp = requests.get(url, proxies=proxies, stream=True,
                                timeout=timeout, headers=HEADERS, verify=False)
            if resp.status_code != 200:
                raise Exception('尝试下载图片时，出现错误，重试' % resp.status_code)
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
        file_path = os.path.join(blogname, '0.'+blogname+' image '+strtime+'.txt')
        self.file = open(file_path, 'w')

    def close(self):
        self.file.close()

    def process_item(self, item):
        if item.get("media"):
            for url in item['media']:
                line = url + '\n'
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
