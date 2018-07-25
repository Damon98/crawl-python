#!usr/bin/env python
#-*- coding:utf-8 -*-

# author Damon Tsui Time: 2018/7/21
import requests
import json
import os
from json import JSONDecodeError
import pymongo
import re
import time
from urllib.parse import urlencode
from hashlib import md5
from multiprocessing import Pool
from bs4 import BeautifulSoup
from config import *


client = pymongo.MongoClient(MONGO_URL,connect=False)
db = client[MONGO_DB]

header = {
    "User-Agent":"Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36"
}

def get_page_index(offset):
    data = {
        'offset': offset,
        'format': 'json',
        'keyword': KEYWORD,
        'autoload': 'true',
        'count': 20,
        'cur_tab': 3,
        'from': 'gallery'
    }
    url = 'https://www.toutiao.com/search_content/' + '?' + urlencode(data)
    try:
        response = requests.get(url, headers=header)
        if response.status_code == 200:
            return response.text
        return None
    except ConnectionError:
        print ('请求索引页错误',url)
        return None

def parse_page_index(html):
    try:
        data = json.loads(html)
        if data and 'data'in data.keys():
            for item in data.get('data'):
                yield item.get('article_url')
    except JSONDecodeError:
        pass

def get_page_detail(url):
    try:
        response = requests.get(url,headers=header)
        if response.status_code == 200:
            return response.text
        return None
    except ConnectionError:
        print('请求详情页错误！',url)
        return None

def parse_page_detail(html,url):
    soup  = BeautifulSoup(html,'lxml')
    result = soup.select('title')
    title = result[0].get_text() if result else ''
    images_pattern = re.compile('gallery: JSON.parse\("(.*)"\)',re.S)
    result = re.search(images_pattern,html)
    if result:
        data = json.loads(result.group(1).replace('\\', ''))
        if data and 'sub_images' in data.keys():
            sub_images = data.get('sub_images')
            images = [item.get('url') for item in sub_images]
            for image in images:download_image(image)
            return {
            'title':title,
            'url': url,
            'images':images
        }

def save_to_mongo(reselt):
    if db[MONGO_TABLE].insert(reselt):
        print('save was done!',reselt)
        return True
    return False

def download_image(url):
    print('正在下载图片',url)
    try:
        response = requests.get(url, headers=header)
        if response.status_code == 200:
            save_image(response.content)
    except ConnectionError:
        print ('请求图片错误',url)
        return None

def save_image(content):
    file_path = '{0}/{1}.{2}'.format(os.getcwd(),md5(content).hexdigest(),'jpg')
    if not os.path.exists(file_path):
        with open(file_path,'wb') as f:
            f.write(content)
            f.close()



def main(offset):
    html = get_page_index(offset)
    for url in parse_page_index(html):
        time.sleep(2)
        html = get_page_detail(url)
        if html:
            result =  parse_page_detail(html,url)
            if result:save_to_mongo(result)



if __name__ == '__main__':
    groups = [x*20 for x in range(GROUP_START, GROUP_END + 1)]
    pool = Pool()
    pool.map(main, groups)
