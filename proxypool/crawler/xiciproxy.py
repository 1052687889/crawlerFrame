#!/usr/bin/env python
# _*_ coding: UTF-8 _*_
# Author:taoke
from lxml import etree
import download
import fake_useragent
import queue
import requests
import re
class xiciproxy(object):
    proxy_server_state = False
    start_urls = 'http://www.xicidaili.com/'
    headers = { 'Host': 'www.xicidaili.com',
                'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:61.0) Gecko/20100101 Firefox/61.0',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-GB,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive'}

    def __init__(self):
        self.ua = fake_useragent.UserAgent()
        self.queue = queue.Queue()

    def wait_proxy_ready(self):
        while True:
            try:
                if self.get_http_proxy() != None:
                    print('web server connect success!!!')
                    self.proxy_server_state = True
                    break
            except:
                pass

    def get_http_proxy(self):
        try:
            t = requests.get('http://127.0.0.1:5000/http').text
            return eval(t)[0]
        except:
            # self.proxy_server_state = False
            pass

    def send_http_proxy_error(self,proxy):
        try:
            t = requests.post('http://127.0.0.1:5000/http',data={'error_proxy':proxy})
        except:
            # self.proxy_server_state = False
            pass

    def start(self):
        self.wait_proxy_ready()
        urls = self.get_page_urls()
        print(list(urls))
        _headers = self.headers
        _headers['User-Agent'] = self.ua.random
        msgs = [(requests.get, self.queue, url, {'headers': _headers,'timeout':10,'proxies': {'http': self.get_http_proxy()}}) for url in urls]
        download.downloader(msgs)
        print('xicidaili ---> start')
        for i in range(len(msgs)):
            res = self.queue.get()
            if res:
                res.encoding = res.apparent_encoding
                for i in self.handle_html(res.text):
                    yield i

    def proxy_requests(self,url):
        while True:
            _headers = self.headers
            _headers['User-Agent'] = self.ua.random
            proxy = self.get_http_proxy()
            if proxy:
                msgs = [(requests.get, self.queue, url,
                         {'headers': _headers, 'timeout': 10, 'proxies': {'http': proxy}})]
            else:
                msgs = [(requests.get, self.queue, url,
                         {'headers': _headers, 'timeout': 10})]
            download.downloader(msgs)
            res = self.queue.get()
            if not res:
                print('get_page_urls error')
                self.send_http_proxy_error(proxy)
            else:
                return res


    def get_page_urls(self):
        try:
            page_num = 10
            res = self.proxy_requests(self.start_urls)
            res.encoding = res.apparent_encoding
            reres = re.findall('<li><a class="false" href="([\s\S]*?)">国内([\s\S]*?)</a></li>', res.text)
            for u in reres:
                for i in range(1, 1 + page_num):
                    print(i)
                    yield self.start_urls + u[0][1:]+ str(i) + '/'
        except Exception as e:
            print('------------------>',e)
            pass

    def safeData(self,data):
        if not data:
            if isinstance(data,list):
                return ['']
            if isinstance(data,str):
                return ''
            if isinstance(data,int):
                return 0
            if isinstance(data,float):
                return 0.0
        else:
            return data

    def handle_html(self, html):
        data_dict = {}
        htmlEmt = etree.HTML(html)
        tr_list = htmlEmt.xpath('//tr')[1:]
        for i in tr_list:
            try:
                IP_PORT = self.safeData(i.xpath('td[2]/text()'))[0]+":"+self.safeData(i.xpath('td[3]/text()'))[0]
                ADDR = self.safeData(i.xpath('td[4]/a/text()'))[0]
                IS_ANONYMOUS = self.safeData(i.xpath('td[5]/text()'))[0]+'代理'
                time = self.safeData(i.xpath('td[10]/text()'))[0]
                ymd = time.split(' ')[0].split('-')
                hour = time.split(' ')[1].split(':')
                SURE_TIME = '20{}年{}月{}日{}时'.format(ymd[0],ymd[1],ymd[2],hour[0])
                data_dict[IP_PORT] = (ADDR,IS_ANONYMOUS,SURE_TIME)
            except Exception as e:
                print('handle_html:',e)
                continue
        for key,value in data_dict.items():
            yield [key,*value,0,0,'xici']



if __name__ == "__main__":
    x = xiciproxy()
    s = x.get_page_urls()
    for i in s:
        print(i)















