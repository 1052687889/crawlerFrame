#!/usr/bin/env python
# _*_ coding: UTF-8 _*_
# Author:taoke
import redis
import utils
class RedisClient(object):
    __HOST = 'localhost'
    __PORT = 6379
    __PASSWORD = None
    __TEMP_BUFFER_KEY = 'TEMP_BUFFER'
    __TEMP_BUFFER_MD5_KEY = 'TEMP_MD5_BUFFER'
    __HTTP_POOL_KEY = "HTTP_POOL_KEY"
    __HTTPS_MD5_KEY = "HTTPS_MD5_KEY"
    __HTTPS_POOL_KEY = "HTTPS_POOL_KEY"
    __HTTP_MD5_KEY = "HTTP_MD5_KEY"

    def __init__(self):
        self.__db = redis.Redis(host=self.__HOST, port=self.__PORT,password=self.__PASSWORD,db=0)

    def recheck(self):
        self.__db.sunion(self.__TEMP_BUFFER_KEY,self.__HTTPS_POOL_KEY,self.__HTTP_POOL_KEY)

        self.__db.delete(self.__HTTP_POOL_KEY)
        self.__db.delete(self.__HTTP_MD5_KEY)
        self.__db.delete(self.__HTTPS_POOL_KEY)
        self.__db.delete(self.__HTTPS_MD5_KEY)

    def adds_temp_buffer(self,iter):
        for proxy in iter:
            m = utils.get_md5(proxy[0].encode())
            if not self.__db.sismember(self.__TEMP_BUFFER_MD5_KEY,m):
                self.__db.sadd(self.__TEMP_BUFFER_KEY,proxy)
                self.__db.sadd(self.__TEMP_BUFFER_MD5_KEY,m)

    def pop_temp_buffer(self):
        reval = self.__db.spop(self.__TEMP_BUFFER_KEY)
        if reval:
            item = eval(reval)
            self.__db.srem(self.__TEMP_BUFFER_MD5_KEY,utils.get_md5(item[0].encode()))
        return reval

    def adds_http_pool(self,iter):
        for proxy in iter:
            m = utils.get_md5(proxy[0].encode())
            if not self.__db.sismember(self.__HTTP_MD5_KEY, m):
                self.__db.sadd(self.__HTTP_POOL_KEY, proxy)
                self.__db.sadd(self.__HTTP_MD5_KEY, m)
                print('http:',proxy)

    def http_pool_move_temp(self,value):
        self.__db.smove(self.__HTTP_POOL_KEY,self.__TEMP_BUFFER_KEY,value)
        self.__db.srem(self.__HTTP_MD5_KEY, utils.get_md5(value.encode()))

    def get_http_one(self):
        reval = self.__db.srandmember(self.__HTTP_POOL_KEY)
        return reval

    def adds_https_pool(self, iter):
        for proxy in iter:
            m = utils.get_md5(proxy[0].encode())
            if not self.__db.sismember(self.__HTTPS_MD5_KEY, m):
                self.__db.sadd(self.__HTTPS_POOL_KEY, proxy)
                self.__db.sadd(self.__HTTPS_MD5_KEY, m)
                print('https',proxy)

    def get_https_one(self):
        reval = self.__db.srandmember(self.__HTTPS_POOL_KEY)
        return reval

    def https_pool_move_temp(self,value):
        self.__db.smove(self.__HTTPS_POOL_KEY, self.__TEMP_BUFFER_KEY, value)
        self.__db.srem(self.__HTTPS_MD5_KEY, utils.get_md5(value.encode()))

    def clear_all(self):
        self.__db.delete(self.__TEMP_BUFFER_KEY)
        self.__db.delete(self.__TEMP_BUFFER_MD5_KEY)
        self.__db.delete(self.__HTTP_POOL_KEY)
        self.__db.delete(self.__HTTP_MD5_KEY)
        self.__db.delete(self.__HTTPS_POOL_KEY)
        self.__db.delete(self.__HTTPS_MD5_KEY)

if __name__ == "__main__":
    rc = RedisClient()
    # rc.clear_all()
    res = rc.pop_temp_buffer()
    print(res)
