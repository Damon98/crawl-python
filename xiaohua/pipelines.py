# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

import os
import time
import random
import scrapy
from xiaohua.settings import IMAGES_STORE as image_store
from scrapy.pipelines.images import ImagesPipeline



class XiaohuaPipeline(ImagesPipeline):

    def get_media_requests(self, item, info):
        image_links = item['src']
        for image_link in image_links:
            # image_link = image_link.decode('utf-8')
            time.sleep(random.randint(1,5))
            yield scrapy.Request(image_link)

    def item_completed(self, results, item, info):
        # print(results)
        image_paths = [x['path'] for ok,x in results if ok]
        if not os.path.exists(image_store + item['alt']):
            os.mkdir(image_store + item['alt'])

        for image_path in image_paths:
            # print(image_store + image_path)
            os.rename(image_store + image_path, image_store + item['alt'] + '/'
                      +  item['alt'] + item['src'][0].split('/')[-1])
        return item



