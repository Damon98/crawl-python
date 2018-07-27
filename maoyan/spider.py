#!usr/bin/env python
#-*- coding:utf-8 -*-

# author Damon Tsui Time: 2018/7/27

from multiprocessing.pool import Pool

import pymongo
import requests
from lxml import etree
from requests import RequestException

from config import *

client = pymongo.MongoClient(MONGO_URL,connect=False)
db = client[MONGO_DB]

header = {
    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'
}

def get_page_index(offset):
    if offset==0:
        url = 'http://maoyan.com/board/4'
    else:
        url = 'http://maoyan.com/board/4' + '?' + 'offset=' + str(offset)
    try:
        response = requests.get(url,headers=header)
        if response.status_code == 200:
            return response.text
        return None
    except RequestException:
        return None

def parse_page_index(html,offset):
    sel = etree.HTML(html)
    for i in range(10):
        title = sel.xpath('//p[@class="name"]/a/text()')[i]
        url = 'maoyan.com' + sel.xpath('//p[@class="name"]/a/@href')[i]
        actors = sel.xpath ('//p[@class="star"]/text()')[i].strip()
        time = sel.xpath ('//p[@class="releasetime"]/text()')[i]
        scores = sel.xpath ('//p[@class="score"]//i/text()')
        score = scores[0] + scores[1]
        result = {
            'index':offset+i+1,
            'title':title,
            'url':url,
            'actors':actors,
            'time':time,
            'score':score,
        }
        if 'index'and 'title'and 'url'and 'actors'and 'time'and 'score' not in result.keys():
            print ('获取数据错!',offset+i+1)

        save_to_mongo(result)

        # with open ('mydy.txt','a', encoding='utf-8') as f:
        #     f.write (json.dumps (result,ensure_ascii=False) + '\n')
        #     f.close ()

def save_to_mongo(result):
    try:
        if db[MONGO_TABLE].insert(result):
            print('存储成功!')
    except Exception:
        print('存储失败!')



def main(offset):
    html = get_page_index(offset)
    parse_page_index(html,offset)


if __name__ == "__main__":
    pool = Pool()
    pool.map(main,[i for i in range(0,100,10)])


