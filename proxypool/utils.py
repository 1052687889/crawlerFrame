#!/usr/bin/env python
# _*_ coding: UTF-8 _*_
# Author:taoke


import hashlib
def get_md5(data):
    m = hashlib.md5()
    m.update(data)
    return m.hexdigest()







if __name__ == "__main__":
    # a = get_md5('1234567890'.encode())
    # print(a)
    print(str(None))

















