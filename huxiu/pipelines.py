# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pymongo

from huxiu.settings import MONGO_URL


class HuxiuPipeline(object):
    def process_item(self, item, spider):
        client = pymongo.MongoClient(MONGO_URL)
        db = client['huxiu']
        flag = 0
        for title in item['title']:
            title = title
            url = item['url'][flag]
            flag += 1
            result = {'title':title,'url':url,'updata':item['updata']}
            try:
                if db['newslist'].insert(result):
                    print('保存成功！')
            except Exception:
                print("保存失败！")
        return item
