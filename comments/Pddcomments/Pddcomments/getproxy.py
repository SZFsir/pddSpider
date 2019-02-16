#! /usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = "JrXnm"
# Date: 18-11-15
# 提供代理IP，在有限代理状态下，尽可能少的被封IP
# 作用是将有效好用的代理ip都放进内存中，取用起来比直接从本地代理池
# requests访问要快得多

import requests
import json
import traceback
import threading
from functools import wraps
import random
import time
from requests.exceptions import ConnectionError, \
    Timeout, ConnectTimeout, ProxyError
from .threadpool import ThreadPool

headers = {
    'Host': 'sports.whu.edu.cn',
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like G'
                  'ecko) Chrome/53.0.2785.104 Safari/537.36 Core/1.53.4843.400 QQBrowser/9.7.13021.400',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1'
}


def synchronous(tlockname):
    """一个基于实例锁的装饰器"""

    def _synched(func):
        @wraps(func)
        def _synchronizer(self,*args, **kwargs):
            tlock = self.__getattribute__( tlockname)
            tlock.acquire()
            try:
                return func(self, *args, **kwargs)
            finally:
                tlock.release()
        return _synchronizer
    return _synched


class Proxy_Ip_Set(object):
    """IP代理类，自动更新ip_set，每次随机get一个ip代理"""

    def __init__(self, proxy_url, crawl_url):
        self.proxy_url = proxy_url
        self.crawl_url = crawl_url
        self.my_lock = threading.RLock()
        self.ip_set = []
        self.bad_ip_set = []
        self.pool = ThreadPool(4)
        self.setup()

    def setup(self):
        print('[+] Proxy Setup！ It is goinging to collect ip proxy')
        ips = self.get_ip_from()

        try:
            for i in range(0, len(ips)):
                ip = ips[i][0]
                ip_port = ips[i][1]
                self.pool.put(self.checkStatus, (ip, ip_port))

            # 等待至少有25个代理
            while len(self.ip_set) < 25:
                print('ffffffffffffffffffffffffffffffffffffffffffffff')
                time.sleep(0.2)

        except Exception as e:
            traceback.print_exc()
            print("error")

        print('eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee')
        # 开启监督进程，调控ip池。
        threading.Thread(target=self.update).start()

    # 检查每个ip代理是否有效
    def checkStatus(self, ip, ip_port):
        proxies = {'http': 'http://{}:{}'.format(ip, ip_port),
                   'https': 'http://{}:{}'.format(ip, ip_port)}
        try:
            r = requests.get(self.crawl_url,
                             headers=headers, proxies=proxies, timeout=2)
            print(str(ip) + ':' + str(ip_port) + '  ', end="")
            print(r)
            if r.status_code == 200:
                if [ip, ip_port] not in self.ip_set:
                    self.ip_set.append([ip, ip_port])
                return True
            else:
                return False
        except (ConnectTimeout, ConnectionError, ProxyError,
                Timeout, ConnectionResetError) as e:
            return False
        except Exception as e:
            print(e)
            return False

    # 在这里定义代理池规则
    def get_ip_from(self):
        url1 = self.proxy_url + ':8000/'
        # url2 = self.proxy_url + ':8888/get_all/'
        # url3 = self.proxy_url + ':5555/get_all/'
        ips = []

        try:
            ip_html = requests.get(url1)
            ips += json.loads(ip_html.text)
        except:
            traceback.print_exc()
            print('ip proxy1 error!!!')

        #try:
        #     ip_html = requests.get(url2)
        #     ip_split = json.loads(ip_html.text)
        #     for ip in ip_split:
        #         ips.append(ip.split(":"))
        # except:
        #     traceback.print_exc()
        #     print('ip proxy2 error!!!')
        #
        # try:
        #     ip_html = requests.get(url3)
        #     ip_split = json.loads(ip_html.text)
        #     for ip in ip_split:
        #         ips.append(ip.split(":"))
        # except:
        #     traceback.print_exc()
        #     print('ip proxy3 error!!!')

        return ips

    def update(self):
        while True:
            # 如果线程池中还有需要检查的ip，暂时不向其中添加
            while self.pool.q.qsize() > 10:
                time.sleep(0.03*len(self.ip_set))
            print('Updating the proxy poll~~~~')
            ips = self.get_ip_from()
            try:
                for i in ips:
                    ip = i[0]
                    ip_port = i[1]
                    self.pool.put(self.checkStatus, (ip, ip_port))

            except Exception as e:
                traceback.print_exc()
                print("error")


    @synchronous('my_lock')
    def get_ip(self):
        ip = random.choice(self.ip_set)
        print("IP 还有 ", len(self.ip_set), "个有效的")
        return ip[0], ip[1], len(self.ip_set)

    @synchronous('my_lock')
    def bad_ip(self, ip):
        try:
            self.ip_set.remove(ip)
        except:
            pass


if __name__ == '__main__':
    proxy_url = 'http://127.0.0.1'
    crawl_url = 'http://apiv3.yangkeduo.com/reviews/14497579/list?page=37&size=10&=1'
    ipset = Proxy_Ip_Set(proxy_url, crawl_url)
    ips = {}

    while True:
        print('len:', len(ipset.ip_set))
        time.sleep(1)




