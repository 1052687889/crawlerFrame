# # -*- coding: utf-8 -*-
# """
# Created on Tue Jul 17 20:08:42 2018
#
# @author: taoke
# """
import user_agent
import requests
import re
import time
from lxml import etree
import db
import random
import multiprocessing
import threadpool
import threading
import queue
import mythread

class AgentsServerCrawler(object):
    def __init__(self,process_num=10):
        self.headers = None
        self.name = ''
        self.url = ""
        self.process_num = process_num
        self.block_ip_port_pool = set()

    def start(self,main_queue):
        pool = multiprocessing.Pool(self.process_num)
        que = multiprocessing.Manager().Queue()
        urls = self.get_page_urls()
        try:
            for index,url in enumerate(urls):
                pool.apply_async(func=self.get_one_page_agentserver,args=(url,index,que))
            pool.close()
            msg_count = 0
            while msg_count < len(urls):
                if not que.empty():
                    msg = que.get()
                    msg_count += 1
                    for m in msg[2]:
                        m.append(self.name)
                        main_queue.put(m)
                        print(m)
            pool.join()
        except TypeError as e:
            print(e,':请填写self.get_page_urls()函数，返回一个可迭代对象')

    def get_one_page_agentserver_hook(self):
        pass

    def get_page_urls(self):
        pass

    def get_one_page_agentserver(self,url,index,queue):
        try:
            html = self.get_html(url=url)
            data = self.handle_html(html=html)
            self.send_msg(queue=queue,index=index,result=True,data=data)
        except:
            self.send_msg(queue=queue, index=index,result=False)

    def get_html(self,url,timeout=10):
        count = 0
        flag = False
        res = None
        while flag == False and count < 3:
            count += 1
            ip_port = AgentsServerPool.random_ip_port(url=url)
            _headers = self.headers
            param = {'url':url, 'timeout':timeout, 'headers':_headers}
            if ip_port:
                param['proxies'] = {url.split(':')[0]:ip_port}
            try:
                res = requests.get(**param)
                res.encoding = res.apparent_encoding
                if re.findall('block',res.text):
                    self.block_ip_port_pool.add(ip_port)
                    raise IOError
                if re.findall('-//W3C//DTD HTML 4.01 Transitional//EN',res.text):
                    raise IOError
                flag = True
            except:
                if not AgentsServerPool.get_num_ip_port(url=url):
                    try:
                        res = requests.get(url=url, timeout=timeout, headers=_headers)
                        res.encoding = res.apparent_encoding
                        flag = True
                    except Exception as e:
                        print('get_html:',url,' ',e)
                        return ''
        return res.text

    def handle_html(self, html):
        return []

    def filter_agentserver(self,datalist,threadNum = 50):
        que = queue.Queue()
        param = zip(list(zip(datalist,[que]*len(datalist))),[None]*len(datalist))
        pool = threadpool.ThreadPool(threadNum)
        reqs = threadpool.makeRequests(self.check_useful,param)
        [pool.putRequest(req) for req in reqs]
        pool.wait()
        revlist = []
        while not que.empty():
            msg = que.get()
            if msg['result'][0] != False or msg['result'][1] != False:
                msg['data'].append(msg['result'][0]) # http
                msg['data'].append(msg['result'][1]) # https
                revlist.append(msg['data'])
        return revlist

    def send_msg(self,queue,index,result,data=[]):
        queue.put((index,result,data))

    def check_useful(self,data,que):
        q = queue.Queue()
        t = threading.Thread(target=self.check_proxy_useful,args=(data[0],q))
        t.start()
        t.join()
        que.put({'data':data,'result':q.get()})

    # http://www.w3school.com.cn/
    @staticmethod
    def check_https_useful(proxy_addr,q):
        try:
            proxies = {'https': proxy_addr}
            res = requests.get(url='https://www.baidu.com', timeout=10, proxies=proxies)
            res.encoding = res.apparent_encoding
            q.put(True if re.findall("<title>百度一下，你就知道</title>", res.text) else False)
        except:
            q.put(False)

    @staticmethod
    def check_http_useful(proxy_addr,q):
        try:
            proxies = {'http': proxy_addr}
            res = requests.get(url='http://www.qq.com/', timeout=10, proxies=proxies)
            res.encoding = res.apparent_encoding
            q.put(True if re.findall("<title>腾讯首页</title>", res.text) else False)
        except:
            q.put(False)

    @staticmethod
    def check_proxy_useful(proxy_addr,que):
        httpq = queue.Queue()
        httpsq = queue.Queue()
        thttp = threading.Thread(target=AgentsServerCrawler.check_http_useful,args=(proxy_addr,httpq))
        thttps = threading.Thread(target=AgentsServerCrawler.check_https_useful, args=(proxy_addr, httpsq))
        thttp.start()
        thttps.start()
        thttp.join()
        thttps.join()
        que.put((httpq.get(),httpsq.get()))

    def get_useful_AgentsServer(self):
        sn = db.DBSession()
        res = sn.session.query(db.AgentServer).all()
        return (item.IP_PORT for item in res)

class _66ip_AgentsServerCrawler(AgentsServerCrawler):
    '''66ip代理'''
    def __init__(self,process_num):
        AgentsServerCrawler.__init__(self,process_num)
        self.name = '66ip'
        self.url = 'http://www.66ip.cn'
        self.headers = { 'Host': 'www.66ip.cn',
                         'Connection': 'keep-alive',
                         'Cache-Control': 'max-age=0',
                         'Upgrade-Insecure-Requests': '1',
                         'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36',
                         'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                         'Referer': 'http://www.66ip.cn/areaindex_5/1.html',
                         'Accept-Encoding': 'gzip, deflate',
                         'Accept-Language': 'zh-CN,zh;q=0.9'}

    def get_page_urls(self):
        '''获取需要爬取页面的urls'''
        try:
            _headers = self.headers
            user_agent.handle_headers(headers=_headers)
            res = requests.get(self.url, headers=_headers)
            res.encoding = res.apparent_encoding
            htmlEmt = etree.HTML(res.text)
            tr_list = htmlEmt.xpath("//ul[@class='textlarge22']/li")[1:]
            return [self.url+i.xpath("a/@href")[0] for i in tr_list]
        except Exception as e:
            print('get_page_urls:',e)

    def handle_html(self, html):
        '''处理html'''
        data_dict = {}
        datalist = []
        htmlEmt = etree.HTML(html)
        tr_list = htmlEmt.xpath('//*[@id="footer"]/div[@align="center"]/table/tr')[1:]
        for tr in tr_list:
            IP_PORT = tr.xpath('td[1]/text()')[0]+':'+tr.xpath('td[2]/text()')[0]
            ADDR = tr.xpath('td[3]/text()')[0]
            IS_ANONYMOUS = tr.xpath('td[4]/text()')[0]
            TIME = tr.xpath('td[5]/text()')[0].split(' ')[0]
            data_dict[IP_PORT] = (ADDR,IS_ANONYMOUS,TIME)
        for key,value in data_dict.items():
            data = [key,*value]
            datalist.append(data)
        revlist = self.filter_agentserver(datalist=datalist)
        return revlist

class xicidaili_AgentsServerCrawler(AgentsServerCrawler):
    '''西刺代理'''
    def __init__(self,process_num):
        AgentsServerCrawler.__init__(self, process_num)
        self.name = 'xicidaili'
        self.encoding = 'utf-8'
        self.url = 'http://www.xicidaili.com/'
        self.headers = { 'Host': 'www.xicidaili.com',
                         'Connection': 'keep-alive',
                         'Cache-Control': 'max-age=0',
                         'Upgrade-Insecure-Requests': '1',
                         'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36',
                         'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                         'Accept-Encoding': 'gzip, deflate',
                          'Accept-Language': 'zh-CN,zh;q=0.9',
                         'If-None-Match': 'W/"6d2996cd67d1f4a3c7acfd76214130ac"'}

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

    def get_page_urls(self,timeout=10):
        try:
            page_num = 10
            user_agent.handle_headers(self.headers)
            text = self.get_html(url=self.url)
            user_agent.handle_headers(self.headers)
            res = requests.get(url=self.url,headers=self.headers,timeout=timeout)
            res.encoding = self.encoding
            reres = re.findall('<li><a class="false" href="([\s\S]*?)">国内([\s\S]*?)</a></li>',text)
            aurl = (self.url + i[0][1:] for i in reres)
            urls = [u+str(i)+'/'for u in aurl for i in range(1,1+page_num)]
            return urls
        except Exception as e:
            print('------------------>',e)
            pass

    def get_one_page_agentserver_hook(self):
        ''' 降低爬取速率，防止服务器被爬蹦 '''
        time.sleep(1)

    def handle_html(self, html):
        data_dict = {}
        datalist = []
        htmlEmt = etree.HTML(html)
        tr_list = htmlEmt.xpath('//tr')[1:]
        for i in tr_list:
            IP_PORT = self.safeData(i.xpath('td[2]/text()'))[0]+":"+self.safeData(i.xpath('td[3]/text()'))[0]
            ADDR = self.safeData(i.xpath('td[4]/a/text()'))[0]
            IS_ANONYMOUS = self.safeData(i.xpath('td[5]/text()'))[0]+'代理'
            time = self.safeData(i.xpath('td[10]/text()'))[0]
            ymd = time.split(' ')[0].split('-')
            hour = time.split(' ')[1].split(':')
            SURE_TIME = '20{}年{}月{}日{}时'.format(ymd[0],ymd[1],ymd[2],hour[0])
            data_dict[IP_PORT] = (ADDR,IS_ANONYMOUS,SURE_TIME)
        for key,value in data_dict.items():
            data = [key,*value]
            datalist.append(data)
        revlist = self.filter_agentserver(datalist=datalist)
        return revlist

class AgentsServerPool(object):
    xicidaili = xicidaili_AgentsServerCrawler(5)
    _66ip = _66ip_AgentsServerCrawler(5)
    AgentsCrawlerList = [xicidaili,_66ip]
    def update_AgentServerSource(self):
        sn = db.DBSession()
        try:
            res = sn.session.query(db.AgentServerSource).all()
            for item in res:
                sn.session.delete(item)
            for item in self.AgentsCrawlerList:
                ass = db.AgentServerSource(SOURCES=item.name,URL=item.url)
                sn.session.add(ass)
            sn.session.commit()
        except Exception as e:
            print('error:',e)
            sn.session.rollback()

    def save_to_sql(self,datalist):
        '''(IP_PORT,ADDR,IS_ANONYMOUS,SURE_TIME)'''
        sn = db.DBSession()
        item_dir = {}
        for item in  datalist:
            try:
                AgentServerSourceitem = item_dir[item[6]]
            except:
                AgentServerSourceitem = sn.session.query(db.AgentServerSource).filter(
                    db.AgentServerSource.SOURCES == item[6]).first()
                item_dir[item[4]] = AgentServerSourceitem
            d = db.AgentServer(IP_PORT=item[0],
                               ADDR=item[1],
                               IS_ANONYMOUS=item[2],
                               SURE_TIME=item[3],
                               HTTP=item[4],
                               HTTPS=item[5],
                               SOURCES=AgentServerSourceitem.SOURCES)
            sn.session.add(d)
        sn.session.commit()
        sn.close()

    def update(self):
        '''通过AgentsCrawlerList更新数据库目标网站url'''
        self.update_AgentServerSource()
        # que = multiprocessing.Queue()
        crawerThreadlist = []
        que = queue.Queue()
        # 创建爬虫对应线程
        for AgentsCrawler in self.AgentsCrawlerList:
            p = threading.Thread(target=AgentsCrawler.start,args=(que,))
            p.start()
            crawerThreadlist.append(p)
        for p in crawerThreadlist:
            p.join()
        # 清除数据库中的代理服务器
        self.clear_AgentServerSql()
        datalist = []
        while not que.empty():
            datalist.append(que.get())
        self.save_to_sql(datalist)

    @staticmethod
    def random_ip_port(url):
        '''从数据库中随机获取代理服务器IP端口'''
        if url[:5] == 'https':
            return AgentsServerPool.random_https_ip_port()
        elif url[:4] == 'http':
            return AgentsServerPool.random_http_ip_port()
        else:
            return None

    @staticmethod
    def random_http_ip_port():
        '''从数据库中随机获取代理服务器IP端口'''
        try:
            sn = db.DBSession()
            http_ip_port_list = sn.session.query(db.AgentServer).filter(db.AgentServer.HTTP==True).order_by().all()
            item = random.choice(http_ip_port_list)
            return item.IP_PORT
        except Exception as e:
            print('random_http_ip_port：',e)
            pass
    @staticmethod
    def get_num_ip_port(url):
        try:
            sn = db.DBSession()
            if url[:5] == 'https':
                return sn.session.query(db.AgentServer).filter(db.AgentServer.HTTPS==True).count()
            elif url[:4] == 'http':
                return sn.session.query(db.AgentServer).filter(db.AgentServer.HTTP==True).count()
            else:
                return None
        except Exception as e:
            print('get_num_ip_port：',e)
            pass
    def get_num_https_ip_port(self):
        try:
            sn = db.DBSession()
            num = sn.session.query(db.AgentServer).filter(db.AgentServer.HTTPS==True).count()
            return num
        except Exception as e:
            print('get_num_https_ip_port：',e)
            pass

    @staticmethod
    def random_https_ip_port():
        '''从数据库中随机获取代理服务器IP端口'''
        try:
            sn = db.DBSession()
            http_ip_port_list = sn.session.query(db.AgentServer).filter(db.AgentServer.HTTPS==True).order_by().all()
            item = random.choice(http_ip_port_list)
            return item.IP_PORT
        except Exception as e:
            print('random_https_ip_port：',e)
            pass

    def clear_AgentServerSql(self):
        '''清除数据库中的代理服务器'''
        sn = db.DBSession()
        try:
            res = sn.session.query(db.AgentServer).all()
            for item in res:
                sn.session.delete(item)
            sn.session.commit()
            return True
        except:
            sn.session.rollback()
            return False

    @staticmethod
    def remove(ip_port):
        '''移除代理服务器'''
        sn = db.DBSession()
        try:
            item = sn.session.query(db.AgentServer).filter(db.AgentServer.IP_PORT == ip_port).one()
            sn.session.delete(item)
            sn.session.commit()
            sn.session.close()
            return True
        except:
            sn.session.rollback()
            return False

if __name__ == "__main__":
    t = time.time()
    crawer = AgentsServerPool()
    crawer.update()
    print('一共花费时间：',time.time()-t,'s')







































































































