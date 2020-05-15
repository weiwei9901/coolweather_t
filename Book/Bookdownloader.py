import random

import redis
import pymongo
import requests
import json
import logging
import threading

from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor

from Proxyer import Proxyer

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")


class BookDownload:
    def __init__(self, chapter_link, start_place=0, abbr='http://', proxy=None):
        self.chapter_link = chapter_link  # 目录页面的链接
        self.start_place = start_place  # 第一章在目录中的位置
        self.abbr_link = abbr  # 前缀 链接的前一部分
        self.redis_client = redis.Redis()
        self.event = threading.Event()
        self.redis_list = 'url_info'
        self.redis_failed_list = 'failed_url'
        self._proxy = proxy
        self.mongo_collect = pymongo.MongoClient().chapter_3.test  # mongodb，自己设置
        self.all_chapter = 0
        self.successed_download = 0
        self.header = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36'}

    @property
    def proxy(self):
        if self._proxy:
            choosed_proxy = random.choice(self._proxy)
            return {'http': 'http:' + choosed_proxy}
        return None

    @proxy.setter
    def proxy(self, value):
        if not isinstance(value, list):
            raise ValueError('must be list type')
        self._proxy = value

    def get_all_chapter(self):
        res = requests.get(self.chapter_link, headers=self.header, timeout=5)

        if res.status_code != 200:
            raise Exception("can't access the website")

        soup = BeautifulSoup(res.content.decode(), 'lxml')
        name_list = soup.find('div', attrs={'id': 'list'})
        dl_list = name_list.find('dl')

        wanted_download = dl_list.find_all('dd')[self.start_place:]
        self.all_chapter = len(wanted_download)

        for order, value in enumerate(wanted_download):
            yield order, value.a.get('href').rsplit('/')[-1], value.a.text

    def store_name_in_redis(self):
        """
        直接调用get_all_chapter
        :return:
        """
        for info in self.get_all_chapter():
            try:
                self.redis_client.rpush(self.redis_list, json.dumps(info))
            except Exception as e:
                logging.info(e)

    def requests_one_link(self, detail_link, timeout):
        """
        直接解析了
        :param detail_link:
        :return: 正文内容
        """

        try:
            res = requests.get(detail_link, proxies=self.proxy, headers=self.header, timeout=timeout)
            text = res.content.decode()
            soup = BeautifulSoup(text, 'lxml')
            zhengwen = soup.find('div', attrs={'id': 'content'}).text.replace(r'<br .*?<.*?>', '\n')
            return zhengwen
        except:
            return None

    def _clear_redis(self):
        """
        清除redis
        :return:
        """
        self.redis_client.ltrim(self.redis_list, 0, 0)
        self.redis_client.lpop(self.redis_list)

        self.redis_client.ltrim(self.redis_failed_list, 0, 0)
        self.redis_client.lpop(self.redis_failed_list)

    def init_work(self):
        self._clear_redis()

    def get_url(self, name):
        """
        从redis中获取url信息
        :return:
        """
        burl_info = self.redis_client.lpop(name)
        if burl_info:
            url_info = json.loads(burl_info)
            order, after_link, name = url_info
            return order, after_link, name
        return None

    def handle(self, order, after_link, name, timeout=2):
        """
        成功不管，失败返回信息扔进failed队列
        :param order:
        :param after_link:
        :param name:
        :return:
        """
        content = self.requests_one_link(self.abbr_link + after_link, timeout)
        if content:
            self.mongo_collect.insert_one({'order': order, 'name': name, 'content': content})
            logging.info('sucess download {}'.format(name))
            self.successed_download += 1
            return None
        else:
            logging.info('failed to download {}'.format(name))
            return order, after_link, name

    def _callback(self, futures):
        """
        回调函数
        :param futures:
        :return:
        """
        res = futures.result()
        if res:
            try:
                self.redis_client.rpush(self.redis_failed_list, json.dumps(res))
            except Exception as e:
                logging.info(e)

    def start_download(self, Pool: ThreadPoolExecutor):
        while True:
            info = self.get_url(self.redis_list)
            if info:
                futures = Pool.submit(self.handle, *info)
                futures.add_done_callback(self._callback)
            else:
                break
        self.event.set()
        Pool.shutdown()

    def failed_download(self):
        """
        对第一次失败的进行下载
        最多尝试三次
        :return:
        """
        if self.event.wait():
            while True:
                info = self.get_url(self.redis_failed_list)
                if info:
                    try_times = 3
                    while try_times:
                        if not self.handle(*info, timeout=3):
                            break
                        try_times -= 1
                else:
                    break
        logging.info("=============end download==============")
        logging.info("===all chapter {}=== success download {}=====".format(self.all_chapter, self.successed_download))

    def start_failed_download(self):
        threading.Thread(target=self.failed_download).start()


if __name__ == '__main__':
    # proxy = Proxyer('http://127.0.0.1:5000/get_all/', proxy_name='proxy')

    Pool = ThreadPoolExecutor(15)
    bookdownload = BookDownload('http://www.xbiquge.la/11/11559/', 0, 'http://www.xbiquge.la/11/11559/')
    bookdownload.init_work()
    bookdownload.store_name_in_redis()
    logging.info('=======================start================================')
    bookdownload.start_download(Pool)
    bookdownload.start_failed_download()
    # print('/llfk/klkn.html'.rsplit('/'))