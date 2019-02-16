# -*- coding: utf-8 -*-
import scrapy
from scrapy import Request
from ..items import PddcommentsItem
from .dboperate import GoodsId, MonggodbOperate
import json

review_url = 'http://apiv3.yangkeduo.com/reviews/%d/list?page=%d&size=20'
review_index_url = "http://yangkeduo.com/goods_comments.html?goods_id=%d"
other_tags = {'-1': '', '-3': 'append', '-4': 'picture', '-5': 'regular_customers'}


class PddcommentsSpider(scrapy.Spider):

    name = 'PDDcomments'
    allowed_domains = ['yangkeduo.com']

    def __init__(self, name=None, **kwargs):
        super().__init__(name, **kwargs)
        # 每个商品类别状态
        self.optset = set(self._loadState())
        self.mongo = MonggodbOperate()

    # 加载状态
    def _loadState(self):
        try:
            state = self.mongo.getState()
        except:
            return []
        return state

    # 重写start_requests,把每个类别的商品id投喂进爬虫
    def start_requests(self):
        state = self._loadState()
        idset = GoodsId()
        print('[++++++++++++++++++++++++++++++]start sql queryyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy!!!!!!!')
        opt_ids = idset.getOpt()
        print('[++++++++++++++++++++++++++++++]finish sql Queryyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy!!!!!!!!')

        for opt in opt_ids:
            if str(opt) in state:
                continue
            goods_ids = idset.getOneOptGoodsId(opt)
            for goods in goods_ids:
                goods_id = goods[0]
                url = review_index_url % goods_id
                request = Request(url, callback=self.parse, priority=opt)
                request.meta['opt'] = opt
                request.meta['goods_id'] = goods_id
                yield request

    def parse(self, response):
        opt = response.meta.get('opt')

        # 找到评论界面最上面的标签
        tags_list = response.xpath("//ul[@id='comment-tag-board-0-ctb-tags']/li")
        goods_id = response.meta.get('goods_id', '')

        #print('[++++++++++++++++++++++++++++++]into parsing')
        if goods_id:
            # 按照标签生成对应评论API
            for lable_tag in tags_list:
                #print('[++++++++++++++++++++++++++++++++++++]parsing {}\'s one tag'.format(goods_id))
                lable_text = lable_tag.xpath("./div/span/text()")
                review_num = int(lable_text.re('\((.*)\)')[0])
                tag = lable_tag.xpath('./@data-tag').extract()[0]
                # 如果是每个商品都可能不同的标签
                if len(tag) == 32:
                    for page in range(1, min(review_num//20 + 2, 51)):
                        url = review_url % (goods_id, page)
                        url += '&label_id=%s' % tag
                        request = Request(url, callback=self.parse_comment, priority=opt)
                        request.meta['goods_id'] = goods_id
                        request.meta['opt'] = opt
                        yield request
                else:  # 如果是都有的标签
                    other_tag_name = other_tags[tag]
                    for page in range(1, min(review_num//20 + 2, 51)):
                        url = review_url % (goods_id, page)
                        url += '&%s=1' % other_tag_name
                        request = Request(url, callback=self.parse_comment, priority=opt)
                        request.meta['goods_id'] = goods_id
                        request.meta['opt'] = opt
                        yield request
                #print('[++++++++++++++++++++++++++++++++++++]end parsing {}\'s one tag'.format(goods_id))

    def parse_comment(self, response):
        opt = response.meta.get('opt', '')

        item = PddcommentsItem()
        data = json.loads(response.text)
        print('opt is', opt)
        print("[++++++++++++++++++++++]insert {}'s comment" .format(response.meta['goods_id']))
        for review in data["data"]:
            item['review_id'] = review.get('review_id', '')
            if not item['review_id']:
                continue
            item['name'] = review.get('name', '')
            item['desc_score'] = review.get('desc_score', None)
            item['logistics_score'] = review.get('logistics_score', None)
            item['service_score'] = review.get('service_score', None)
            item['specs'] = str(review.get('specs', []))
            item['avatar'] = review.get('avatar', '')
            item['goods_id'] = response.meta['goods_id']
            item['comment'] = review.get('comment', '')
            item['stars'] = review.get('stars', None)
            item['opt'] = opt

            yield item


if __name__ == '__main__':
    db = GoodsId()

    optsort = db.getOpt()
    print(optsort)
    i = optsort.index(5163)
    print(optsort[i+1])
    #print(db.getOneOptGoodsId('2607'))

    # with open('opt_id.txt', 'r') as f:
    #     f.read