#!/usr/bin/env python
# _*_ coding: UTF-8 _*_
# Author:taoke
import hashlib
class url_manager(object):
    def __init__(self):
        self.url_md5_set = set()

    def is_handled(self,url):
        m = self.get_md5(url.encode('utf-8'))
        return m in self.url_md5_set

    def get_md5(self,data):
        if isinstance(data,bytes):
            m = hashlib.md5()
            m.update(data)
            return int(m.hexdigest(),base=16)
        else:
            raise ValueError(data)

    def add_url(self,url):
        self.url_md5_set.add(self.get_md5(url.encode('utf-8')))

    def get_count(self):
        return len(self.url_md5_set)
















