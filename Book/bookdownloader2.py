'''

安装redis  开启server
采用redis 数据太多好像一次取不出来 试了一个一万多章的,一次只取出了9000多章, 现在分批次取
所以大概需要的值有两个
1. 所需要爬取小说的目录页面的链接
2. 第一章的开头位置, 因为有些可能前六章是最新章节 默认:0
3.有问题再说

'''

import random
import time

import redis
# import pymongo
import requests
import json
import logging
import threading

from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor

# from Proxyer import Proxyer

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")


class BookDownload:
    def __init__(self, chapter_link, start_place=0, abbr='http://', proxy=None):
        self.chapter_link = chapter_link  # 目录页面的链接
        self.start_place = start_place  # 第一章在目录中的位置
        self.abbr_link = chapter_link.rsplit('/',1)[0] + '/'  # 前缀 链接的前一部分 做了处理 不需要再传了
        self.redis_client = redis.Redis()
        self.event = threading.Event()
        self.redis_list = 'url_info'
        self.redis_failed_list = 'failed_url'
        self.redis_cache = 'download'
        self._proxy = proxy
        # self.mongo_collect = pymongo.MongoClient().chapter_3.test3  # mongodb，自己设置
        self.all_chapter = 0
        self.successed_download = 0
        self.encoding = None
        self.session = requests.session()
        self.header = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36'}

    @property
    def proxy(self):
        # 代理质量好就用代理 免费代理不推荐(本机就行) 测试的这个网站不咋封ip
        # 要求传递list or None
        if self._proxy:
            choosed_proxy = random.choice(self._proxy)
            return {'http': 'http:' + choosed_proxy}
        return None

    @proxy.setter
    def proxy(self, value):
        if isinstance(value, list) or value is None:
            self._proxy = value
        else:
            raise ValueError('must be list type or None')

    def get_all_chapter(self):
        res = self.session.get(self.chapter_link, headers=self.header, timeout=5)
        if res.status_code != 200:
            raise Exception("can't access the website")
        # print(res.encoding)
        self.encoding = res.encoding if res.encoding in {'utf8','utf-8','gbk'} else 'utf8'
        # print(self.encoding)
        soup = BeautifulSoup(res.content.decode(self.encoding), 'lxml')
        # print(soup.prettify())
        name_list = soup.find('div', attrs={'id': 'chapterlist'})
        # dl_list = name_list.find('dl')

        wanted_download = name_list.find_all('p')[self.start_place:]
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

            res = self.session.get(detail_link, proxies=self.proxy, headers=self.header, timeout=timeout)
            text = res.content.decode(self.encoding)
            soup = BeautifulSoup(text, 'lxml')
            # print(soup.prettify())
            zhengwen = soup.find('div', attrs={'id': 'chaptercontent'}).text.replace(r'<br .*?<.*?>', '')
            return zhengwen
        except Exception as e:
            print(detail_link)
            raise e
            # return None

    def _clear_redis(self):
        """
        清除redis
        :return:
        """
        try:
            self.redis_client.ltrim(self.redis_list, 0, 0)
            self.redis_client.lpop(self.redis_list)

            self.redis_client.ltrim(self.redis_failed_list, 0, 0)
            self.redis_client.lpop(self.redis_failed_list)

            self.redis_client.zremrangebyrank(self.redis_cache, 0, 9999)
            # self.redis_client.lpop(self.redis_cache)
        except Exception as e:
            pass

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
            keys = name + '\n' + content
            self.redis_client.zadd(self.redis_cache, {keys: order})
            logging.info('sucess download {}'.format(name))
            self.successed_download += 1
            # self.mongo_collect.insert_one({'order': order, 'name': name, 'content': content})
            # logging.info('sucess download {}'.format(name))
            # self.successed_download += 1
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
        thread = threading.Thread(target=self.failed_download)
        thread.start()
        thread.join()

    def store_txt(self):
        txt = self.chapter_link.split('/')[-2] + '.txt'

        # count = self.redis_client.zcard(self.redis_cache)
        while self.redis_client.zcard(self.redis_cache):
            content = ''
            for x in self.redis_client.zrange(self.redis_cache, 0, 1000):
                content += x.decode() + '\n'
            with open(txt, 'w') as f:
                f.write(content)
            self.redis_client.zremrangebyrank(self.redis_cache, 0, 1000)


if __name__ == '__main__':
    Pool = ThreadPoolExecutor(10)
    bookdownload = BookDownload('http://m.xianqihaotianmi.com/book_14852/all.html', 0)
    bookdownload.init_work()
    bookdownload.store_name_in_redis()
    logging.info('=======================start================================')
    bookdownload.start_download(Pool)
    bookdownload.start_failed_download()
    bookdownload.store_txt()
