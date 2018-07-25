#!usr/bin/env python
#-*- coding:utf-8 -*-

# author Damon Tsui Time: 2018/7/23
import json
import re
import time
from json import JSONDecodeError
from multiprocessing import Pool
from urllib.parse import urlencode
import pymongo
import requests
from config import *

client = pymongo.MongoClient(MONGO_URL, connect=False)
db = client[MONGO_DB]

header = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36",
}

def get_page_index():

    url = 'http://36kr.com'
    try:
        response = requests.get(url, headers=header)
        if response.status_code == 200:
            return response.text
        return None
    except ConnectionError:
        print('获取首页出错', url)
        return None

def parse_page_index(html):
    try:
        data = re.compile('<script>var props=(.*?)</script>',re.S)
        contains = re.search(data,html).group(1)
        str_data = re.sub (',locationnal=.*', '', contains)
        data_list = json.loads(str_data)['feedPostsLatest|post']
        if data_list:
            for item in data_list:
                title = item['title']
                url = 'http://36kr.com/p/' + item['id'] + '.html'
                result_index = {
                    'title' : title,
                    'url' : url
                }
                save_to_mongo(result_index)
        return None
    except JSONDecodeError:
        pass


def get_page_next(page):
    data = {
        'per_page': 20,
        'page': page,
        '_': int(round(time.time() * 1000))
    }
    url = 'http://36kr.com/api/search-column/mainsite' + '?' + urlencode(data)
    try:
        time.sleep(1)
        response = requests.get(url, headers=header)
        if response.status_code == 200:
            return response.text,url
        return None
    except ConnectionError:
        print('获取下一页的链接出错！',url)
        return None

def parse_page_next(data,url):
    data = json.loads(data)
    if data and 'data' in data.keys():
        items = data.get('data')
        for item in items.get('items'):
            try:
                title = item['title']
                url = 'http://36kr.com/p/' + str(item['id']) + '.html'
                tag = item['extraction_tags']
                summary = item['summary']
                published_time = item['published_at']
                result_next = {
                    'title': title,
                    'url': url,
                    'tag': tag,
                    'summary': summary,
                    'published_time': published_time,
                }
            except KeyError:
                print('获取数据出错！')
            print (url)
            save_to_mongo (result_next)
        return None


def save_to_mongo(i):
    try:
        if db[MONGO_TABLE].insert(i):
            print('存储成功！')
    except Exception:
        print('存储失败！')


def main():
    # 首页内容的爬取
    html = get_page_index()
    parse_page_index(html)
    # 加载页的爬取
def next_page(page):
    data, url = get_page_next(page)
    parse_page_next(data, url)

if __name__ == '__main__':
    main()
    pool = Pool()
    group = [i for i in range(GROUP_START, GROUP_END)]
    pool.map(next_page, group)
