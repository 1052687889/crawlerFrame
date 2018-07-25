#!/usr/bin/env python
# _*_ coding: UTF-8 _*_
# Author:taoke
import threading

class myThread(threading.Thread):
    def __init__(self,func,args=()):
        super(myThread,self).__init__()
        self.func = func
        self.args = args

    def run(self):
        self.result = self.func(*self.args)

    def get_result(self):
        try:
            return self.result
        except Exception:
            return None








