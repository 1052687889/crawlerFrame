#!/usr/bin/env python
# _*_ coding: UTF-8 _*_
# Author:taoke
import urllib
import requests
import user_agent
import json
import os
import url_manager
import pathlib
import multiprocessing


class baiduimgCrawler(object):
    url = 'https://image.baidu.com/search/index'
    headers = {
                'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                'Accept-Encoding':'gzip, deflate, br',
                'Accept-Language':'zh-CN,zh;q=0.9',
                'Cache-Control':'max-age=0',
                'Connection':'keep-alive',
                'Host':'image.baidu.com',
                'Upgrade-Insecure-Requests':'1',
                'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36'}

    jsonformdata = {'tn': 'resultjson_com',
                    'ipn': 'rj',
                    'ct': '201326592',
                    'is':'',
                    'fp': 'result',
                    'queryWord': '',
                    'cl': '2',
                    'lm': '-1',
                    'ie': 'utf-8',
                    'oe': 'utf-8',
                    'adpicid':'',
                    'st':'-1',
                    'z':'',
                    'ic':'0',
                    'word': '',
                    's':'',
                    'se':'',
                    'tab':'',
                    'width':'',
                    'height':'',
                    'face':'0',
                    'istype': '2',
                    'qc':'',
                    'nc':'1',
                    'fr':'',
                    'cg': 'girl',
                    'pn':'0',
                    'rn': '30',
                    'gsm': '78',
                    '1532007256185':''}

    def __init__(self,target,allnum):
        self.manager = url_manager.url_manager()
        self.target = target
        self.count = 0
        self.urls = []
        self.allnum = allnum
        if not os.path.exists('./img'):
            os.makedirs('./img')
        if not os.path.exists('./img/'+target):
            os.makedirs('./img/'+target)

    def start(self):
        page_num = 0
        que = multiprocessing.Manager().Queue()
        pool = multiprocessing.Pool(10)
        while self.allnum > self.manager.get_count():
            urls = self.get_img_url(page_num)
            page_num += 1
            for url in urls:
                if self.allnum < self.manager.get_count():
                    break
                else:
                    if not self.manager.is_handled(url):
                        self.manager.add_url(url)
                        pool.apply_async(func=self.download_img,args=(url,self.count,que,))
                        self.count += 1
        pool.close()
        msg_count = 0
        while self.allnum > msg_count:
            if not que.empty():
                msg = que.get()
                msg_count += 1
                if msg[1] == 'error':
                    print('{}/{}    {}:{}'.format(msg_count,self.allnum,msg[1],msg[2]))
                else:
                    print('{}/{}    {}'.format(msg_count, self.allnum, msg[1]))

        pool.join()

    def get_img_url(self,n):
        try:
            user_agent.handle_headers(self.headers)
            self.jsonformdata['pn'] = str(int(self.jsonformdata['rn']) * n)
            self.jsonformdata['word'] = self.target
            self.jsonformdata['queryWord'] = self.target
            u = 'https://image.baidu.com/search/acjson?' + urllib.parse.urlencode(self.jsonformdata)
            r = requests.get(u, headers=self.headers)
            r.encoding = 'utf-8'
            j = json.loads(r.text)
            revlist = []
            revlist += [i['thumbURL'] for i in j['data'] if i]
            return revlist
        except Exception as e:
            print('get_img_url:',e)
            return []

    def save_img(self,path,content):
        with open(path,'wb') as file:
            file.write(content)

    def get_img_content(self,url):
        return requests.get(url,timeout=15).content

    def get_img_path(self,url,count):
        path = pathlib.Path(__file__).parent/'img'/'{}'.format(self.target)/'{}.{}'.format(count,url.split('.')[-1])
        return path

    def download_img(self,url,count,queue):
        try:
            img_path = self.get_img_path(url,count)
            img_content = self.get_img_content(url)
            self.save_img(img_path,img_content)
            queue.put((count,'sussess',url))
        except Exception as e:
            print('download_img:',e)
            queue.put((count, 'error',url))

if __name__ == "__main__":
    b = baiduimgCrawler('车牌号',500)
    b.start()
















