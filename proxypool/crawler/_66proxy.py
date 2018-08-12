#!/usr/bin/env python
# _*_ coding: UTF-8 _*_
# Author:taoke
from lxml import etree
import download
import fake_useragent
import queue
import requests
class _66proxy(object):

    start_urls = 'http://www.66ip.cn'
    headers = { 'Host': 'www.66ip.cn',
                'Connection': 'keep-alive',
                'Cache-Control': 'max-age=0',
                'Upgrade-Insecure-Requests': '1',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                'Referer': 'http://www.66ip.cn/areaindex_5/1.html',
                'Accept-Encoding': 'gzip, deflate',
                'Accept-Language': 'zh-CN,zh;q=0.9'}

    def __init__(self):
        self.ua = fake_useragent.UserAgent()
        self.queue = queue.Queue()

    def start(self):
        urls = self.get_page_urls()
        _headers = self.headers
        _headers['User-Agent'] = self.ua.random
        msgs = [(requests.get, self.queue, url, {'headers': _headers,'timeout':10}) for url in urls]
        download.downloader(msgs)
        for i in range(len(msgs)):
            res = self.queue.get()
            if res:
                res.encoding = res.apparent_encoding
                for i in self.handle_html(res.text):
                    yield i

    def handle_html(self, html=''):
        '''处理html'''
        data_dict = {}
        htmlEmt = etree.HTML(html)
        tr_list = htmlEmt.xpath('//*[@id="footer"]/div[@align="center"]/table/tr')[1:]
        for tr in tr_list:
            IP_PORT = tr.xpath('td[1]/text()')[0]+':'+tr.xpath('td[2]/text()')[0]
            ADDR = tr.xpath('td[3]/text()')[0]
            IS_ANONYMOUS = tr.xpath('td[4]/text()')[0]
            TIME = tr.xpath('td[5]/text()')[0].split(' ')[0]
            data_dict[IP_PORT] = (ADDR,IS_ANONYMOUS,TIME)
        for key,value in data_dict.items():
            yield [key,*value,0,0,'66ip']

    def get_page_urls(self):
        '''获取需要爬取页面的urls'''
        try:
            _headers = self.headers
            _headers['User-Agent'] = self.ua.random
            msgs = [(requests.get, self.queue, self.start_urls, {'headers': _headers})]
            download.downloader(msgs)
            res = self.queue.get()
            if res:
                res.encoding = res.apparent_encoding
                htmlEmt = etree.HTML(res.text)
                tr_list = htmlEmt.xpath("//ul[@class='textlarge22']/li")[1:]
                return (self.start_urls+i.xpath("a/@href")[0] for i in tr_list)
            else:
                return []
        except Exception as e:
            print('get_page_urls:',e)


if __name__ == "__main__":
    s = _66proxy()
    urls = s.start()
    for i in urls:
        print(i)
























