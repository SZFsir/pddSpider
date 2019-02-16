#! /usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = "JrXnm"
# Date: 18-12-1

import re
from time import ctime
import json
import threading
import traceback
from urllib.parse import urlparse, parse_qs
from core.threadpool import ThreadPool
from core.proxy import RspIntercept, AsyncMitmProxy, ReqIntercept
from core.dboperate import DbOperate


class RspInterceptor(RspIntercept, ReqIntercept):

    def deal_response(self, response):
        if response.request.hostname == 'apiv3.yangkeduo.com' and response.status == 200:
            pa = re.compile(r'v4/operation/[0-9]*/groups')
            res = pa.findall(response.request.path)
            if res:
                try:
                    parse_tp.put(parse.parse_goods, (json.loads(str(response.get_body_data(),
                                                            encoding='utf-8')), response.request.path))
                except:
                    print(response.request.path)
                    traceback.print_exc()
        elif response.request.hostname != 'apiv3.yangkeduo.com'and response.status == 200:
            try:
                good = json.loads(str(response.get_body_data(), encoding='utf-8'))
                g = good.get('goods_list', '')
                g.get('goods_id', '')
                if g:
                    print(response.request.path)
                    print(good)
            except:
                pass
        if response.request.hostname == 'yangkeduo.com' and response.status == 200:
            pa = re.compile(r'catgoods.html\?.*opt_id')
            res = pa.findall(response.request.path)
            if res:
                try:
                    parse_tp.put(parse.parse_top_opt, (response.request.path, ))
                except:
                    print(response.request.path)
                    traceback.print_exc()

        if '.js' in response.request.path:
            js_body = response.get_body_str('utf-8')
            js_body = js_body.replace('sourceMappingURL=', '')
            response.set_body_str(js_body, 'utf-8')

        if 'react_psnl_verification_' in response.request.path:
            js_body = str(response.get_body_data(), 'utf-8')
            js_body =  js_body.replace("navigator.webdriver", "navigator.qwerasdfzxcv")
            response.set_body_data(bytes(js_body, 'utf-8'))

        return response

    def deal_request(self, request):
        # print(request.get_body_data())
        #
        # request.set_header('DNT', '1')
        # print(request.get_headers())
        return request


class Parse(object):
    def __init__(self):
        self.urlset = set()

    def parse_top_opt(self, thread_name, url):
        parsed_url = urlparse(url)
        query = parse_qs(parsed_url.query)
        opt_id = query['opt_id'][0]

        if (int(opt_id), ) not in IDSETs[2]:
            IDSETs[2].add((int(opt_id), ))
            opt_name = query['opt_name'][0]
            db_tp.put(dbo.insertTopOpts, (opt_id, opt_name))

    def parse_goods(self, thread_name, goodlist, url):
        global Dupli
        if url not in self.urlset:
            self.urlset.add(url)
        else:
            return
        pa = re.compile(r'operation/(.*?)/groups')
        top_opts = pa.findall(url)
        if top_opts:
            top_opt = top_opts[0]
            goods = goodlist.get('goods_list', '')
            if goods:
                for g in goods:
                    goods_id = g.get('goods_id', '')
                    if not goods_id:
                        break
                    if (int(goods_id), ) in IDSETs[0]:
                        Dupli += 1
                        continue
                    goods_name = g.get('goods_name', '')
                    hd_thumb_url = g.get('hd_thumb_url', '')
                    country = g.get('country', '')
                    event_type = g.get('event_type', '')
                    mall_name = g.get('mall_name', '')
                    group_price = str(int(g.get('group', '')['price'])/100)
                    cnt = g.get('cnt', '')
                    normal_price = str(int(g.get('normal_price', ''))/100)
                    market_price = str(int(g.get('market_price', ''))/100)
                    short_name = g.get('short_name', '')
                    # print(goods_id, goods_name, hd_thumb_url, country, event_type,
                    #       mall_name, group_price, cnt, normal_price, market_price, short_name, opt)

                    db_tp.put(dbo.insertgoods, (goods_id, goods_name, hd_thumb_url, country, event_type,
                                    mall_name, group_price, cnt, normal_price, market_price, short_name, top_opt))
                    IDSETs[0].add((goods_id, ))
                print('Parsed a goods')

            # dbo.insertTopOpts(top_opt, '')
            opts = goodlist.get('opt_infos', '')
            if opts:
                for lopt in opts:
                    id = lopt.get('id', '')
                    if not id:
                        continue
                    if (int(id), ) not in IDSETs[1]:
                        IDSETs[1].add((int(id), ))
                        opt_name = lopt.get('opt_name', '')
                        db_tp.put(dbo.insertOpts, (id, opt_name, top_opt))


def Monitor():
    global Dupli
    while True:
        try:
            print('Dupli = ', Dupli)
            print(ctime(), 'IDSET = ', len(IDSETs[0]), len(IDSETs[1]), len(IDSETs[2]))
            print(ctime(), 'dbQueue = ', db_tp.q.qsize())
            print(ctime(), 'parseQueue = ', parse_tp.q.qsize())
            ins = input()
        except:
            traceback.print_exc()


def loadIdSet():
    IDSET = dbo.getallidlist()
    return IDSET


if __name__ == "__main__":
    dbo = DbOperate()
    IDSET = loadIdSet()
    IDSETs = [set(IDSET.get('goods', ())), set(IDSET.get('opts', ())), set(IDSET.get('top_opts', ()))]
    Dupli = 0
    parse = Parse()
    # 解析线程池
    parse_tp = ThreadPool(2)
    # 数据库操作线程池,
    db_tp = ThreadPool(1)
    threading.Thread(target=Monitor).start()
    baseproxy = AsyncMitmProxy(server_addr=('', 8888), https=True)
    baseproxy.register(RspInterceptor)
    baseproxy.serve_forever()



