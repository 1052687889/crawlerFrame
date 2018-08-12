#!/usr/bin/env python
# _*_ coding: UTF-8 _*_
# Author:taoke
import threading
import threadpool
import queue
import multiprocessing
class downloader(object):
    __manage_threading = None
    __msg_buffer = queue.Queue()
    __threading_queue = queue.Queue()
    __threading_num = 100
    pool = threadpool.ThreadPool(__threading_num)
    def __init__(self,msgs):
        for msg in msgs:
            # (func,url,queue,**kwargs)
            self.__msg_buffer.put(msg)
        if not self.__manage_threading:
            self.__manage_threading = threading.Thread(target=self.__manage_downloader)
            self.__manage_threading.start()

    def __manage_downloader(self):
        while not self.__msg_buffer.empty():
            msgs_temp = []
            count = self.__msg_buffer.qsize()
            while not self.__msg_buffer.empty():
                msgs_temp.append((None,{'msg':self.__msg_buffer.get()}))
            requests = threadpool.makeRequests(self.__requests, msgs_temp)
            [self.pool.putRequest(req) for req in requests]
            while count != 0:
                m = self.__threading_queue.get()
                m[1].put(m[0])
                count -= 1
            self.pool.wait()
        self.__manage_threading = None

    def __requests(self,msg):
        try:
            # print(msg[2],msg[3])
            respond =msg[0](msg[2],**msg[3])
        except IndexError:
            respond = msg[0](msg[2])
        except Exception as e:
            print('->',e)
            respond = None
        self.__threading_queue.put((respond,msg[1]))

if __name__ == "__main__":
    import requests
    q = queue.Queue()
    url = 'https://www.baidu.com'
    # headers = { 'Host': 'www.66ip.cn',
    #             'Connection': 'keep-alive',
    #             'Cache-Control': 'max-age=0',
    #             'Upgrade-Insecure-Requests': '1',
    #             'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36',
    #             'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    #             'Referer': 'http://www.66ip.cn/areaindex_5/1.html',
    #             'Accept-Encoding': 'gzip, deflate',
    #             'Accept-Language': 'zh-CN,zh;q=0.9'}
    def get_https_proxy():
        try:
            t = requests.get('http://127.0.0.1:5000/https').text
            return eval(t)[0]
        except:
            pass
    msgs = [(requests.get,q,url,{'proxies': {'http': get_https_proxy()}}) for i in range(20)]
    # requests.get().status_code
    downloader(msgs)
    downloader(msgs)
    downloader(msgs)
    print(threading.active_count())
    for i in range(1000):
        if i == 35:
            downloader(msgs)
        m = q.get()
        if m:
            m.encoding = m.apparent_encoding
            print(i,m.status_code)
        else:
            print(i, m)
    print('threading count:',threading.active_count())























