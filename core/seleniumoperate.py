#! /usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = "JrXnm"
# Date: 18-11-30

import time
import random
import re
import json
import base64
import traceback
from core.captcha import Chaojiying_Client
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
from selenium.common.exceptions import NoSuchElementException
from utils.threadpool import ThreadPool

tokens = []



cookie1 = {
            'name': 'PDDAccessToken',
            'domain': '.yangkeduo.com',
            "expires": "",
            'path': '/',
            'httpOnly': False,
            'HostOnly': False,
            'Secure': False
        }
url = 'http://yangkeduo.com/classification.html'


class CaptchaMonitor(object):
    """验证码处理监控总类"""

    def __init__(self):
        self.checklist = []
        self.loopexam = False
        self.chaojiying = Chaojiying_Client('username', 'password', '6001')

    # 检查是否正在等待输入验证码
    @staticmethod
    def isWaitForCapcha(browser):
        try:
            inputed = browser.find_element_by_xpath('//input[@id="captchaInput"]')
            img = browser.find_element_by_xpath('//div[@class="captcha"]/img')
            imgs = img.get_attribute('src')

            if inputed and imgs:
                return True
            else:
                return False
        except:
            return False

    def checkCaptcha(self, browser):
        # 若检测不到商品， 要么是出现验证码， 要么是异常(大多是因为网络延时问题)。
        for i in range(3):
            cap = self.isWaitForCapcha(browser)
            if cap:
                # 如果两次输入验证码时间小于三分钟，丢弃这个窗口。
                if self.checklist:
                    timedelay = (datetime.now() - self.checklist[-1]).seconds
                    if timedelay < 180:
                        self.loopexam = True
                print('wait for exam')
                cap_res = self.manageCaptcha(browser)
                if not cap_res:
                    return False
                else:
                    return True
            else:
                print('Some thing Wrong with result = 0!!!')
                time.sleep(2)
        return False

    # 验证码处理程序
    def manageCaptcha(self, browser):
        print('In captcha process')
        # 记录本窗口输入验证码的时间
        now = datetime.now()
        self.checklist.append(now)

        for i in range(4):
            time.sleep(3)
            # 获得验证码
            img = browser.find_element_by_xpath('//div[@class="captcha"]/img')
            imgs = img.get_attribute('src')
            imgs = imgs.replace('data:image/jpeg;base64,', '')
            raw = base64.b64decode(imgs)
            print('get the captcha')

            # 从打码平台获取验证码，发送并接受反馈
            inputed = browser.find_element_by_xpath('//input[@id="captchaInput"]')
            cap = self.chaojiying.PostPic(raw, 6001)
            pic_str = cap.get('pic_str', '')
            pic_id = cap.get('pic_id', '')
            inputed.send_keys(pic_str)
            confirm = browser.find_element_by_xpath('//div[@class="confirm button"]')
            confirm.click()
            print('send the code')

            checkloop = self.captchaCheckLoop(browser)
            time.sleep(3)
            # 若打码错误，则发送错误，继续重新获取。超过4次返回异常。
            # 若出现
            try:
                img = browser.find_element_by_xpath('//div[@class="captcha"]/img')
                if img and not checkloop:
                    self.chaojiying.ReportError(pic_id)
                    browser.reflash()
                elif img and checkloop:
                    self.loopexam = True
                    return False
                else:
                    return True
            except NoSuchElementException:
                return True
            except:
                pass
        return False

    # 爬取时间一长，会对同一个账号不断地出现验证码，检测是否有验证循环出现
    @staticmethod
    def captchaCheckLoop(browser):
        print('check for loop')
        pa = re.compile(r'catgoods.html')
        for i in range(70):
            url = browser.current_url
            #print(url)
            res = pa.findall(url)
            if res:
                print('loop')
                return True
            time.sleep(0.05)
        return False


class PDDSelenium(object):
    """ 拼多多自动化浏览类， 各种浏览方式，配合连接代理，在代理中抓取。 """

    def __init__(self, proxy_ip='127.0.0.1', proxy_port=8888):
        self.proxy_ip = proxy_ip
        self.proxy_port = proxy_port
        self.profile = self._setProfile()
        self.state = self._loadState()

    # 加载爬取信息上次保存状态
    @staticmethod
    def _loadState():
        try:
            with open('state', 'r') as f:
                state = json.load(f)
        except:
            traceback.print_exc()
            return None
        return state

    # 保存状态信息
    def _saveState(self):
        try:
            with open('state', 'w') as f:
                json.dump(self.state, f)
        except:
            traceback.print_exc()

    # 设置代理
    def _setProfile(self):
        profile = FirefoxProfile()
        profile.set_preference('permissions.default.image', 2)
        profile.set_preference("network.proxy.type", 1)
        profile.set_preference("network.proxy.http", self.proxy_ip)
        profile.set_preference("network.proxy.http_port", self.proxy_port)
        return profile

    @staticmethod
    def singleGoodDrop(thread_name, browser, caps):
        while True:
            print('scroll Down')
            browser.execute_script("window.scrollTo(0,document.body.scrollHeight)")
            time.sleep(1)
            pa = re.compile(r'<div class="cell" style')
            res = pa.findall(browser.page_source)

            res1 = len(res)
            print(thread_name, len(res))
            # 若检查出加载到底，或者五次滑动都不再变化时停止对本页面爬取
            for k in range(5):
                # 若出现商品为空的情况，将控制权交给验证码验证处理程序
                if not res:
                    check_cap = caps.checkCaptcha(browser)
                    if caps.loopexam:
                        browser.close()
                    if not check_cap:
                        browser.refresh()
                # 若滑动加载与上次一相同，等待
                if len(res) > 0 and len(res) == res1:
                    print(thread_name, 'wait')
                    browser.execute_script("window.scrollTo(0,document.body.scrollHeight)")
                    time.sleep(2)
                    res1 = len(res)
                    res = pa.findall(browser.page_source)
                else:
                    break
            # 检测是否到达底下了
            try:
                if '没有更多了...' in browser.page_source:
                    print(thread_name, '没有更多了...')
                    time.sleep(8)
                    break
            except NoSuchElementException:
                pass
        return res

    # 对第n个分类处商品信息进行爬取
    def cateGoods(self, thread_name, m, ):

        cookies = cookie1
        cookies['value'] = random.choice(tokens)
        options = webdriver.FirefoxOptions()
        # 设置火狐为无头浏览器（即关闭显示）
        options.add_argument('-headless')
        options.add_argument('--disable-gpu')
        # 初始化selenium
        browser = webdriver.Firefox(firefox_profile=self.profile, firefox_options=options)
        browser.get(url)
        browser.delete_all_cookies()
        browser.add_cookie(cookies)
        browser.get(url)

        # 初始化验证码管理类
        caps = CaptchaMonitor()

        point = browser.find_elements_by_xpath('//li[@class="detail-item"]')
        print('cates', len(point))
        point[m].click()
        print('qqqq')

        total_len = 0
        i = 0
        while True:
            # 不断地下拉直至最底部
            res = self.singleGoodDrop(thread_name, browser, caps)
            total_len += len(res)
            print('total len', total_len)
            # 如果还存在小分类目录继续爬取
            try:
                cats = browser.find_elements_by_xpath('//li[@class="fixed-nav-item-catgoods"]')
                cats[i].click()
            except:
                traceback.print_exc()
                break
            lenc = len(cats)
            print('lenc', lenc)
            i += 1
            if i > lenc:
                break

        print(thread_name, 'total len', total_len)
        browser.close()

        # 处理完一个小分类即刻保存状态
        goods_down = self.state.get('goods_down', [])
        goods_down.append(m)
        goods_down = list(set(goods_down))  # 去重
        self.state['goods_down'] = goods_down
        self._saveState()

    # 爬虫任务调度
    def cateGoodsControl(self, n):
        # 恢复爬取状态
        tp = ThreadPool(n)
        while True:
            state = self._loadState()
            leave_list = list(range(183))
            if state:
                goods_down = state.get('goods_down', [])
                leave_list = list(set(leave_list) - set(goods_down))

            j = 0
            for i in leave_list:
                print(i)
                tp.put(self.cateGoods, (i,))
                if j == 0:
                    time.sleep(60)
                    j = 1


if __name__ == '__main__':

    pdd = PDDSelenium()
    pdd.cateGoodsControl(3)



