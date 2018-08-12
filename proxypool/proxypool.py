#!/usr/bin/env python
# _*_ coding: UTF-8 _*_
# Author:taoke
from flask import Flask,render_template,request
import re
import requests
import queue
from download import downloader
from database import RedisClient
from crawler import _66proxy,xiciproxy
import threading
import time
import sys
class ProxyPool(object):
    MAX_ERROR_NUM = 2
    def __init__(self):
        self.db = RedisClient()
        # self.db.recheck()
        # self.db.clear_all()
        self.crawlers = [xiciproxy.xiciproxy()] #,xiciproxy.xiciproxy()_66proxy._66proxy(),
        self.check_task = threading.Thread(target=self.check_useful_task)
        self.check_task.daemon = True
        self.check_task.start()
        self.check_task = threading.Thread(target=self.interface)
        self.check_task.daemon = True
        self.check_task.start()
        self.update()

    def update(self):
        threading.Thread(target=self.get_data).start()

    def get_data(self):
        for crawler in self.crawlers:
            self.db.adds_temp_buffer(crawler.start())

    def start_one_check(self,check_buffer,eval_data,type):
        assert type == 'http' or type == 'https','type 为 http或者https'
        if type == 'http':
            msgs = [(requests.get, queue.Queue(), 'http://www.qq.com', {'timeout': 5, 'proxies': {'http': eval_data[0]}}), ]
            check_buffer.append((eval_data, msgs[0][1], 'http',))
        else:
            msgs = [(requests.get, queue.Queue(), 'https://www.baidu.com',{'timeout': 5, 'proxies': {'https': eval_data[0]}}), ]
            check_buffer.append((eval_data, msgs[0][1], 'https'))
        return msgs

    def check_useful_task(self):
        check_buffer = []
        count = 0
        while True:
            count += 1
            data = self.db.pop_temp_buffer()
            if data:
                eval_data = eval(data)
                if eval_data[4] < self.MAX_ERROR_NUM and eval_data[5] < self.MAX_ERROR_NUM:
                    if count // 2:
                        msgs = self.start_one_check(check_buffer,eval_data,'http')
                    else:
                        msgs = self.start_one_check(check_buffer, eval_data, 'https')
                else:
                    if eval_data[4] < self.MAX_ERROR_NUM:
                        msgs = self.start_one_check(check_buffer, eval_data, 'http')
                    elif eval_data[5] < self.MAX_ERROR_NUM:
                        msgs = self.start_one_check(check_buffer, eval_data, 'https')
                    else:
                        continue
                downloader(msgs)
            else:
                for item in check_buffer:
                    if not item[1].empty():
                        res = item[1].get()
                        if res:
                            res.encoding = res.apparent_encoding
                            if item[2] == 'http':
                                if re.findall("<title>腾讯首页</title>", res.text):
                                    item[0][4] = self.MAX_ERROR_NUM
                                    self.db.adds_http_pool(((*item[0][:4],0,item[0][6]),))
                                else:
                                    item[0][4] += 1
                            elif item[2] == 'https':
                                if re.findall("<title>百度一下，你就知道</title>", res.text):
                                    item[0][5] = self.MAX_ERROR_NUM
                                    self.db.adds_https_pool(((*item[0][:4],0,item[0][6]),))
                                else:
                                    item[0][5] += 1
                        else:
                            if item[2] == 'http':
                                item[0][4] += 1
                            elif item[2] == 'https':
                                item[0][5] += 1

                        if item[0][4] < self.MAX_ERROR_NUM or item[0][5] < self.MAX_ERROR_NUM:
                            self.db.adds_temp_buffer((item[0],))

                        check_buffer.remove(item)
                time.sleep(0.01)

    def interface(self):
        while True:
            instr = input('>>>')
            if instr == 'exit':
                sys.exit()
            elif instr == 'get_http_one':
                print(self.db.get_http_one())
            elif instr == 'get_https_one':
                print(self.db.get_https_one())
            else:
                print('请重新输入')


if __name__ == "__main__":
    __all__ = ['app']
    app = Flask(__name__)

    @app.route('/')
    def index():
        return 'index'

    @app.route('/http',methods = ['POST','GET'])
    def http_Proxy():
        if request.method == "POST":
            proxy = request.form.get('error_proxy')
            pool.db.http_pool_move_temp(proxy)
            return u'POST' + '+' + 'error_proxy' + '+' + proxy
        else:
            reval =  pool.db.get_http_one()
            if reval:
                return str(eval(reval))
            else:
                return str(None)

    @app.route('/https',methods = ['POST','GET'])
    def https_Proxy():
        if request.method == "POST":
            proxy = request.form.get('error_proxy')
            pool.db.https_pool_move_temp(proxy)
        else:
            reval =  pool.db.get_https_one()
            if reval:
                return str(eval(reval))
            else:
                return str(None)

    pool = ProxyPool()
    app.run()

















