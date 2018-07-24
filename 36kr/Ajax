#!usr/bin/env python
#-*- coding:utf-8 -*-

# author Damon Tsui Time: 2018/7/23
'''
爬取36氪首页
'''

import json
import re
import requests


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
    data = re.compile('<script>var props=(.*?)</script>',re.S)
    contains = re.search(data,html).group(1)
    str_data = re.sub (',locationnal=.*', '', contains)
    data_list = json.loads(str_data)['feedPostsLatest|post']
    for item in data_list:
        title = item['title']
        url = 'http://36kr.com/p/' + item['id'] + '.html'
        yield {
            'title' : title,
            'url' : url
        }



def main():
    html = get_page_index()
    result = parse_page_index(html)
    print([i for i in result])


if __name__ == '__main__':
    main()
