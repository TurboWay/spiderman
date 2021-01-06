#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time : 2021/1/5 17:20
# @Author : way
# @Site : 
# @Describe: 布隆过滤器

import importlib
from hashlib import md5
from scrapy_redis.dupefilter import RFPDupeFilter


class BloomFilter:

    def __init__(self, server=None, key='BloomFilter', bloom_num=1, bloom_mem=256, bloom_k=7):
        """
        :param server: redis instance
        :param key: redis key
        :param bloom_num: 布隆过滤器个数，由于 bloom_mem 有大小限制，可以增加过滤器个数进行负载
        :param bloom_mem: 布隆过滤器内存大小（单位: M），不能超过 512 M （ Redis一个String最大只能 512M ）
        :param bloom_k: 哈希次数，次数越少，去重速度越快，但漏失率越大
        """
        self.redis = server
        self.key = key
        self.bloom_num = bloom_num
        self.mem = bloom_mem
        self.k = bloom_k
        self.m = self.mem * 8 * 1024 * 1024
        SEEDS = [5, 7, 11, 13, 31, 37, 61]
        self.seeds = SEEDS[: self.k]

    def add(self, value):
        key = self.key + str(int(self.md5(value)[0:2], 16) % self.bloom_num)
        for seed in self.seeds:
            hash = self.hash(value, seed)
            self.redis.setbit(key, hash, 1)

    def is_exist(self, value):
        exist = True
        key = self.key + str(int(self.md5(value)[0:2], 16) % self.bloom_num)
        for seed in self.seeds:
            hash = self.hash(value, seed)
            exist = exist & self.redis.getbit(key, hash)
        return exist

    def hash(self, value, seed):
        ret = 0
        value = self.md5(value)
        for i in value:
            ret += seed * ret + ord(i)
        return (self.m - 1) & ret

    def md5(self, value):
        md5_str = md5()
        md5_str.update(value.encode())
        return md5_str.hexdigest()


class BloomRFDupeFilter(RFPDupeFilter):

    def __init__(self, server, key, debug=False):
        super().__init__(server, key, debug)
        self.server = server
        self.key = key.replace('dupefilter', 'bloomfilter')
        self.debug = debug
        self.logdupes = True
        spidername = self.key.split(':')[0]
        module_name = f'SP.spiders.{spidername}'
        module = importlib.import_module(module_name)
        spider = getattr(module, f'{spidername}_Spider')
        bloom_num = spider.custom_settings.get('BLOOM_NUM', 1)
        bloom_mem = spider.custom_settings.get('BLOOM_MEM', 256)
        bloom_k = spider.custom_settings.get('BLOOM_K', 7)
        self.bf = BloomFilter(server=self.server, key=self.key, bloom_num=bloom_num, bloom_mem=bloom_mem, bloom_k=bloom_k)
        self.logger.info(f"已启用布隆过滤器，过滤器 {self.key}，个数为 {self.bf.bloom_num} 个，大小为 {self.bf.mem} M，哈希次数为 {self.bf.k} 次")

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
