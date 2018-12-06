#! /usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = "JrXnm"
# Date: 18-12-1
import pymysql
import traceback


class DbOperate(object):
    """Class for Database Operater"""

    def __init__(self):
        db = pymysql.connect('127.0.0.1', 'root', '123456', 'PDD')
        cursor = db.cursor()
        self.db = db
        self.cursor = cursor

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
            self.cursor.execute(sql)
            self.db.commit()
            return True
        except:
            traceback.print_exc()

    def insertTopOpts(self, thread_name, id, opt_name):
        try:
            opt_name = pymysql.escape_string(opt_name)
            sql = "INSERT INTO top_opt VALUES('%s','%s')" % (id, opt_name)
            self.cursor.execute(sql)
            self.db.commit()
        except:
            traceback.print_exc()

    def insertOpts(self, thread_name, id, opt_name, fa_opt):
        try:
            opt_name = pymysql.escape_string(opt_name)
            sql = "INSERT INTO opt VALUES('%s','%s','%s')" % (id, opt_name, fa_opt)
            self.cursor.execute(sql)
            self.db.commit()
        except:
            traceback.print_exc()

    def getallidlist(self):
        try:
            sql = "SELECT goods_id FROM goods"
            self.cursor.execute(sql)
            goods_ids = self.cursor.fetchall()

            sql = "SELECT id FROM opt"
            self.cursor.execute(sql)
            opt_ids = self.cursor.fetchall()

            sql = "SELECT id FROM top_opt"
            self.cursor.execute(sql)
            topopt_ids = self.cursor.fetchall()

            return {'goods': goods_ids, 'opts': opt_ids, 'top_opts': topopt_ids}
        except:
            traceback.print_exc()



if __name__ == '__main__':
    d = DbOperate()
    print(d.getgoodsidlist())
    d.insertgoods('1234567','','','','','','','','','','',111)

