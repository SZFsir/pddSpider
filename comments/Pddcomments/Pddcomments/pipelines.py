# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pymongo
import requests
import hashlib
from scrapy.exceptions import DropItem
import threading
from functools import wraps


class PddcommentsPipeline(object):
    def process_item(self, item, spider):
        return item


def synchronous(tlockname):
    """一个基于实例锁的装饰器"""

    def _synched(func):
        @wraps(func)
        def _synchronizer(self, *args, **kwargs):
            tlock = self.__getattribute__(tlockname)
            tlock.acquire()
            try:
                return func(self, *args, **kwargs)
            finally:
                tlock.release()
        return _synchronizer
    return _synched


class DuplicatePipeline(object):
    """实现去重，因为只有在每个单独商品内部才可能
    存在评论重复，所以仅仅在商品部分去重"""

    def __init__(self):
        self.singlegoods = {}
        #self.lock = threading.RLock()

    def process_item(self, item, spider):
        goods_id = item.get('goods_id', None)
        review_id = item.get('review_id')

        if goods_id and review_id:
            if goods_id not in self.singlegoods.keys():
                self.singlegoods[goods_id] = set()

            if review_id in self.singlegoods[goods_id]:
                raise DropItem('Duplicate!')
            else:
                self.singlegoods[goods_id].add(review_id)

        return item

    # @synchronous('lock')
    # def delete_goods(self):
    #     self.singlegoods.pop(0)
    #     self.sortgoodsid.pop(0)


class MongoDbPipeline(object):

    def __init__(self, mongo_uri, mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db
        self.opt_count = {}
        self.count = 0

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings.get('MONGO_URI'),
            mongo_db=crawler.settings.get('MONGO_DB')
        )

    # 获得每次收集状态的最后一个值，将最后一个给删除掉重新爬取
    def get_state(self):
        try:
            state = self.db['count'].find_one()
            state.pop('_id')
            minopt = 10000
            for opt in state.keys():
                minopt = min(minopt, int(opt))
            state.pop(str(minopt))
            self.opt_count.update(state)
        except:
            self.opt_count.update({})

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]
        self.get_state()

    def process_item(self, item, spider):
        item['avatar_hash'] = self.hash_images(item['avatar'])
        if item['avatar_hash']:
            opt = item.get('opt', None)
            if opt:
                if str(opt) not in self.opt_count.keys():
                    self.opt_count[str(opt)] = 0
                else:
                    self.opt_count[str(opt)] += 1
            if self.count % 1000 == 0:
                self.db['count'].remove({})
                self.db['count'].insert(self.opt_count)
            # print("insert %d's comment %s" % (item['goods_id'], item['name']))
            self.count += 1
            item_dic = dict(item)
            item_dic.pop('opt')
            self.db['comments'].insert(item_dic)
        return item

    @staticmethod
    def hash_images(image_url):
        try:
            image = requests.get(image_url, timeout=3)
            image_raw = image.content
            image_hash = hashlib.md5()
            image_hash.update(image_raw)
            image_hash = image_hash.hexdigest()
            return image_hash
        except:
            return False

    def close_spider(self, spider):
        self.client.close()

