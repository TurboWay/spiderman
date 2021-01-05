#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time : 2021/1/5 17:20
# @Author : way
# @Site : 
# @Describe: 布隆过滤器 参考 https://blog.csdn.net/Bone_ACE/article/details/53107018

from hashlib import md5
from scrapy_redis.dupefilter import RFPDupeFilter

SEEDS = [5, 7, 11, 13, 31, 37, 61]


class BloomFilter:

    def __init__(self, server=None, key='BloomFilter'):
        self.mem = 256   # 设定布隆过滤器内存大小（单位: M），默认 256 M，可以满足 0.98亿条字符串的去重，漏失率为 0.000112
        self.k = 7
        self.m = self.mem * 8 * 1024 * 1024
        self.seeds = SEEDS[: self.k]
        self.key = key
        self.redis = server

    def add(self, value):
        for seed in self.seeds:
            hash = self.hash(value, seed)
            self.redis.setbit(self.key, hash, 1)

    def is_exist(self, value):
        exist = True
        for seed in self.seeds:
            hash = self.hash(value, seed)
            exist = exist & self.redis.getbit(self.key, hash)
        return exist

    def hash(self, value, seed):
        ret = 0
        md5_str = md5()
        md5_str.update(value.encode())
        value = md5_str.hexdigest()
        for i in value:
            ret += seed * ret + ord(i)
        return (self.m - 1) & ret


class BloomRFDupeFilter(RFPDupeFilter):

    def __init__(self, server, key, debug=False):
        super().__init__(server, key, debug)
        self.server = server
        self.key = key.replace('dupefilter', 'bloomfilter')
        self.debug = debug
        self.logdupes = True
        self.bf = BloomFilter(server=self.server, key=self.key)
        self.logger.info(f"已启用布隆过滤器，过滤器 {self.key} 大小为 {self.bf.mem} M")

    def request_seen(self, request):
        fp = self.request_fingerprint(request)
        if self.bf.is_exist(fp):  # 判断存在
            return True
        else:
            self.bf.add(fp)  # 如果不存在，将请求添加到 Redis
            return False

# if __name__ == '__main__':
#     import redis
#     from SP.settings import REDIS_HOST, REDIS_PORT
#     server = redis.Redis(host=REDIS_HOST, port=REDIS_PORT)
#     bf = BloomFilter(server=server, key='zhifang:BloomFilter')
#     bf.add('www.baidu.com')
#     bf.add('www.taobao.com')
#     print(bf.is_exist('www.taobao.com'))
