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

class AgentsServerCrawler(object):
    def __init__(self,process_num=10):
        self.headers = None
        self.name = ''
        self.url = ""
        self.process_num = process_num
        self.encoding = 'utf-8'

    def start(self):
        pool = multiprocessing.Pool(self.process_num)
        que = multiprocessing.Manager().Queue()
        urls = self.get_page_urls()
        try:
            for index,url in enumerate(urls):
                pool.apply_async(func=self.get_one_page_agentserver,args=(url,index,que,self.encoding))
            pool.close()
            msg_count = 0
            while msg_count < len(urls):
                if not que.empty():
                    msg = que.get()
                    msg_count += 1
                    self.save_to_sql(msg[2])
                    for m in msg[2]:
                        print(m)
            pool.join()
        except TypeError as e:
            print(e,':请填写self.get_page_urls()函数，返回一个可迭代对象')

    def get_one_page_agentserver_hook(self):
        pass

    def get_page_urls(self):
        pass

    def get_one_page_agentserver(self,url,index,queue,encoding='utf-8'):
        try:
            html = self.get_html(url=url,encoding=encoding)
            self.get_one_page_agentserver_hook()
            data = self.handle_html(html=html)
            self.send_msg(queue=queue,index=index,result=True,data=data)
        except:
            self.send_msg(queue=queue, index=index,result=False)

    def get_html(self,url,timeout=10,encoding='utf-8'):
        ip_port = AgentsServerPool.random_ip_port()
        _headers = self.headers
        param = {'url':url, 'timeout':timeout, 'headers':_headers}
        if ip_port:
            proxies = {'http': ip_port, 'https': ip_port}
            param['proxies'] = proxies
        try:
            res = requests.get(**param)
        except:
            AgentsServerPool.remove(ip_port)
            res = requests.get(url=url, timeout=timeout, headers=_headers)
        res.encoding = encoding
        return res.text

    def handle_html(self, html):
        return []

    def filter_agentserver(self,datalist,threadNum = 10):
        pool = threadpool.ThreadPool(threadNum)
        reqs = threadpool.makeRequests(self.check_useful,datalist)
        for num in range(len(datalist)):
            if not reqs[num]:
                datalist.remove(num)
        pool.wait()
        return datalist


    def send_msg(self,queue,index,result,data=[]):
        queue.put((index,result,data))

    def check_useful(self,data):
        return self.check_proxy_useful(data[0],"http://www.baidu.com")

    def save_to_sql(self,datalist):
        '''(IP_PORT,ADDR,IS_ANONYMOUS,SURE_TIME)'''
        sn = db.DBSession()
        AgentServerSourceitem = sn.session.query(db.AgentServerSource).filter(
            db.AgentServerSource.SOURCES == self.name).first()
        for item in  datalist:
            d = db.AgentServer(IP_PORT=item[0],
                               ADDR=item[1],
                               IS_ANONYMOUS=item[2],
                               SURE_TIME=item[3],
                               SOURCES=AgentServerSourceitem.SOURCES)
            sn.session.add(d)
        sn.session.commit()
        sn.close()

    # 通过监控百度服务器的返回信息来检测代理服务器是否可用
    @staticmethod
    def check_proxy_useful(proxy_addr, url):
        try:
            proxies = {'http': proxy_addr, 'https': proxy_addr}
            res = requests.get(url=url, timeout=10, proxies=proxies)
            res.encoding = 'utf-8'
            return True if re.findall("<title>百度一下，你就知道</title>", res.text) else True
        except:
            return False

    def get_useful_AgentsServer(self):
        sn = db.DBSession()
        res = sn.session.query(db.AgentServer).all()
        return (item.IP_PORT for item in res)

class _66ip_AgentsServerCrawler(AgentsServerCrawler):
    '''66ip代理'''
    def __init__(self,process_num):
        AgentsServerCrawler.__init__(self,process_num)
        self.encoding = 'gb2312'
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
            res.encoding = 'gb2312'
            htmlEmt = etree.HTML(res.text)
            tr_list = htmlEmt.xpath("//ul[@class='textlarge22']/li")[1:]
            return [self.url+i.xpath("a/@href")[0] for i in tr_list]
        except Exception as e:
            print('error:',e)

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
        self.filter_agentserver(datalist=datalist)
        return datalist


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

    def get_page_urls(self):
        try:
            page_num = 50
            user_agent.handle_headers(self.headers)
            res = requests.get(url=self.url,headers=self.headers)
            res.encoding = self.encoding
            reres = re.findall('<li><a class="false" href="([\s\S]*?)">国内([\s\S]*?)</a></li>',res.text)
            aurl = (self.url + i[0][1:] for i in reres)
            urls = [u+str(i)+'/'for u in aurl for i in range(1,1+page_num)]
            return urls
        except:
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
        self.filter_agentserver(datalist=datalist)
        return datalist

class AgentsServerPool(object):
    AgentsCrawlerList = [xicidaili_AgentsServerCrawler(10), _66ip_AgentsServerCrawler(10)]

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

    def update(self):
        '''通过AgentsCrawlerList更新数据库目标网站url'''
        self.update_AgentServerSource()
        crawerthreadlist = []
        # 清除数据库中的代理服务器
        self.clear_AgentServerSql()
        # 创建爬虫对应线程
        for AgentsCrawler in self.AgentsCrawlerList:
            t = threading.Thread(target=AgentsCrawler.start)
            t.start()
            crawerthreadlist.append(t)
        for crawerthread in crawerthreadlist:
            crawerthread.join()

    @staticmethod
    def random_ip_port():
        '''从数据库中随机获取代理服务器IP端口'''
        try:
            sn = db.DBSession()
            count = sn.session.query(db.AgentServer).count()
            i = random.randint(1,count+1)
            item = sn.session.query(db.AgentServer).filter(db.AgentServer.id == i).first()
            return item.IP_PORT
        except Exception as e:
            # print('没有数据：',e)
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

    def remove(self,ip_port):
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
    crawer = AgentsServerPool()
    # crawer.update()
    print(crawer.random_ip_port())











































































































