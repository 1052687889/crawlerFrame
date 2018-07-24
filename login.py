#!/usr/bin/env python
# _*_ coding: UTF-8 _*_
# Author:taoke
# from selenium import webdriver
# import time
# driver = webdriver.Chrome()
# driver.get('https://index.baidu.com/#/')
#
# driver.find_element_by_xpath('//*[@id="home"]/div[1]/div[2]/div[1]/div[4]/span/span').click()
# time.sleep(0.5)
# driver.find_element_by_xpath('//*[@id="TANGRAM__PSP_4__userName"]').send_keys('1052687889')
# driver.find_element_by_xpath('//*[@id="TANGRAM__PSP_4__password"]').send_keys('1994414110hy')
# driver.find_element_by_xpath('//*[@id="TANGRAM__PSP_4__submit"]').click()
# time.sleep(1)
# if driver.find_element_by_xpath('//*[@id="TANGRAM__14__header_h3"]'):
#     while True:
#         driver.find_element_by_xpath('//*[@id="TANGRAM__14__button_send_mobile"]').click()
#         s = input('请输入登录验证码：')
#         driver.find_element_by_xpath('//*[@id="TANGRAM__14__input_vcode"]').send_keys(s)
#         driver.find_element_by_xpath('//*[@id="TANGRAM__14__button_submit"]').click()
#         time.sleep(1)
#         if not driver.find_element_by_xpath('//*[@id="TANGRAM__14__header_h3"]'):
#             break
import requests
import user_agent
class baidu_login(object):
    def get_headers(self):
        headers = {
                    # 'Host': 'passport.baidu.com',
                    # 'Connection': 'keep-alive',
                    # 'Content-Length': '2145',
                    # 'Cache-Control': 'max-age=0',
                    # 'Origin': 'http://www.baidu.com',
                    # 'Upgrade-Insecure-Requests': '1',
                    # 'Content-Type': 'application/x-www-form-urlencoded',
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                    # 'Referer': 'http://www.baidu.com/',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'Accept-Language': 'zh-CN,zh;q=0.9',
                    }
        return user_agent.handle_headers(headers)

    def get_url(self):
        return 'http://www.baidu.com/'

    def get_html(self,url):
        html = requests.session().get(url=url,headers=self.get_headers())
        # html = requests.get(url=url,headers=self.get_headers()).text
        return html


if __name__ == '__main__':
    b = baidu_login()
    # print(b.get_html(b.get_url()))
    # print(requests.get('https://www.baidu.com',headers=b.get_headers()).text)
    # s = requests.Session()
    # print(s.get(url='https://www.baidu.com', verify=True).text)
    # print(s.headers)
    # print()
    print(requests.get('https://www.baidu.com/', verify=False).content)






