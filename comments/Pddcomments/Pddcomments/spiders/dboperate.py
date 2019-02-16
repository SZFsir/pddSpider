#! /usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = "JrXnm"
# Date: 18-12-14
# 本文件两个数据库操作类主要是用作爬虫调度和断开重连使用

import pymongo
import pymysql


class GoodsId(object):
    """Class For Get Goods Id"""

    def __init__(self):
        db = pymysql.connect('127.0.0.1', 'root', '123456', 'PDD')
        cursor = db.cursor()
        self.db = db
        self.cursor = cursor

    @staticmethod
    def getOpt():
        try:
            with open('opt_id.txt', 'r') as f:
                opt_ids = f.readlines()
            for i in range(len(opt_ids)):
               opt_ids[i] = int(opt_ids[i].rstrip('\n'))
            optsorted = sorted(opt_ids)
            optsorted.reverse()
            return optsorted
        except:
            print('error')

    def getOneOptGoodsId(self, opt_id):
        try:
            sql = "SELECT goods_id FROM goods WHERE opt=%s" % opt_id
            self.cursor.execute(sql)
            goods_ids = self.cursor.fetchall()
            return goods_ids
        except:
            pass

    def scheduleForGoodsId(self):
        pass


class MonggodbOperate(object):

    def __init__(self):
        self.client = pymongo.MongoClient('localhost')
        self.db = self.client['PDDComments']

    def deleteOnegoods(self, goods_id):
        self.db['comments'].remove({'goods_id': goods_id})

    def getOneGoods(self, goods_id):
        good = self.db['comments'].find_one({'goods_id': goods_id})
        return good

    def getState(self):
        try:
            state = self.db['count'].find_one()
            state.pop('_id')
            minopt = 10000
            for opt in state.keys():
                minopt = min(minopt, int(opt))
            state.pop(str(minopt))
            return list(state.keys())
        except:
            return []


if __name__ == '__main__':
    d = GoodsId()
    print(d.getOpt())
# def deleteOneopt(opt):
#     d = GoodsId()
#     m = MonggodbOperate()
#     goodss = d.getOptGoodsList(opt)
#
#     for goods in goodss:
#         m.deleteOnegoods(goods[0])
