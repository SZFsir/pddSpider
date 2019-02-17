#! /usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = "JrXnm"
# Date: 18-12-1
import pymysql
import traceback
import pymongo


class DbOperate(object):
    """Class for Database Operater"""

    def __init__(self):
        db = pymysql.connect('127.0.0.1', 'jrxnm', '123456', 'pdd')
        self.db = db

    def insertgoods(self, thread_name, goods_id, goods_name, hd_thumb_url, country, event_type,
                    mall_name, group_price, cnt, normal_price, market_price, short_name, opt):
        try:
            goods_name = pymysql.escape_string(goods_name)
            hd_thumb_url = pymysql.escape_string(hd_thumb_url)
            country = pymysql.escape_string(country)
            mall_name = pymysql.escape_string(mall_name)
            short_name = pymysql.escape_string(short_name)
            sql = "INSERT INTO goods VALUES" \
                  "('%s', '%s', '%s', '%s', '%s', '%s', '%s', " \
                  "'%s', '%s', '%s', '%s', '%s')" % (goods_id, goods_name, hd_thumb_url,
                                               country, event_type, mall_name, group_price,
                                               cnt, normal_price, market_price, short_name, opt)
            cursor = self.db.cursor()
            cursor.execute(sql)
            cursor.close()
            self.db.commit()
            return True
        except:
            traceback.print_exc()

    def insertTopOpts(self, thread_name, id, opt_name):
        try:
            opt_name = pymysql.escape_string(opt_name)
            sql = "INSERT INTO top_opt VALUES('%s','%s')" % (id, opt_name)
            cursor = self.db.cursor()
            cursor.execute(sql)
            cursor.close()
            self.db.commit()
        except:
            traceback.print_exc()

    def insertOpts(self, thread_name, id, opt_name, fa_opt):
        try:
            opt_name = pymysql.escape_string(opt_name)
            sql = "INSERT INTO opt VALUES('%s','%s','%s')" % (id, opt_name, fa_opt)
            cursor = self.db.cursor()
            cursor.execute(sql)
            cursor.close()
            self.db.commit()
        except:
            traceback.print_exc()

    def getallidlist(self):
        try:
            sql = "SELECT goods_id FROM goods"
            cursor = self.db.cursor()
            cursor.execute(sql)
            goods_ids = cursor.fetchall()


            sql = "SELECT id FROM opt"
            cursor.execute(sql)
            opt_ids = cursor.fetchall()

            sql = "SELECT id FROM top_opt"
            cursor.execute(sql)
            topopt_ids = cursor.fetchall()
            cursor.close()

            return {'goods': goods_ids, 'opts': opt_ids, 'top_opts': topopt_ids}
        except:
            traceback.print_exc()

    def getOptGoodsList(self, opt):
        try:
            sql = "SELECT * from goods WHERE opt={}".format(opt)
            cursor = self.db.cursor()
            cursor.execute(sql)
            goods = cursor.fetchall()
            cursor.close()
            return goods
        except:
            traceback.print_exc()

    def getOptGoodsCntSum(self, opt):
        try:
            sql = "SELECT sum(cnt) FROM goods WHERE opt={}".format(opt)
            cursor = self.db.cursor()
            cursor.execute(sql)
            sums = cursor.fetchall()[0]
            cursor.close()
            return sums
        except:
            traceback.print_exc()


class MonggodbOperate(object):

    def __init__(self):
        self.client = pymongo.MongoClient('localhost')
        self.db = self.client['PDDComments']

    def deleteOnegoods(self, goods_id):
        self.db['comments'].remove({'goods_id': goods_id})

    def getOneGoods(self, goods_id):
        good = self.db['comments'].find_one({'goods_id': goods_id})
        return good

    def statetest(self):
        state = self.db['count'].find_one()
        print(state)
        state.pop('_id')
        print(state)


def getCommentAverage(dic):
    sums = 0
    goods_lens = 0
    for opt in dic.keys():
        cnt_sum = d.getOptGoodsCntSum(opt)
        goods_len = len(d.getOptGoodsList(opt))
        goods_lens += goods_len
        sums += int(cnt_sum[0])

    revs = 0
    for rev in dic.values():
        revs += rev

    print(sums, revs, goods_lens, revs / goods_lens, sums / revs)


def deleteOneopt(opt):
    goodss = d.getOptGoodsList(opt)

    for goods in goodss:
        # print(goods[0])
        # print(m.getOneGoods(goods[0]))
        m.deleteOnegoods(goods[0])


if __name__ == '__main__':
    d = DbOperate()
    m = MonggodbOperate()
   # print(d.getgoodsidlist())
    d.insertgoods('123','123456789','','','','','','',123,'','','',111)
    
    # dic = {
    #     "6212": 1380, "6214": 4153, "6235": 33939, "6220": 69071, "6219": 122326, "6210": 21516, "6209": 10202,
    #     "6218": 34763, "6211": 254, "6251": 58, "6234": 38856, "6215": 1457, "6276": 15950, "6277": 3143, "6197": 36413,
    #     "6213": 1083, "6250": 7196, "6203": 53787, "6217": 317, "6204": 2430, "6216": 2834
    # }
    # getCommentAverage(dic)
    #deleteOneopt('6219')
    #m.statetest()





