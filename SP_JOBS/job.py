#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time : 2019/4/4 10:42
# @Author : way
# @Site : all
# @Describe: 基础类

from scrapy.cmdline import execute
from SP.utils.make_jobs import ScheduledRequest, RedisCtrl


class SPJob:

    def __init__(self, spider_name):
        self.spider_name = spider_name
        self.redis_key = f'{spider_name}:start_urls'
        self.redis_dupefilter = f'{spider_name}:dupefilter'
        self.redis_requests = f'{spider_name}:requests'
        self.reqs = []

    # 生成任务，执行爬虫
    def run_job(self, pages):
        self.make_job(pages)
        execute(['scrapy', 'crawl', self.spider_name])

    # 生成任务
    def make_job(self, pages):
        for pagenum in range(1, pages + 1):
            req = ScheduledRequest(
                url='',  # 请求地址
                method='',  # 请求方式  GET/POST
                callback='',  # 回调函数标识
                body={'pagenum': pagenum,  # 页码
                      'sitename': 'sitename',  # 站点名称
                      # 如果是POST，post的表单也放这边
                      }
            )
            self.reqs.append(req)
        self.push()

    # 将任务推到redis
    def push(self):
        redisctrl = RedisCtrl()
        redisctrl.reqs_push(self.redis_key, self.reqs)
        self.reqs.clear()

    # 删除redis上一次残留任务
    def delete(self):
        redisctrl = RedisCtrl()
        redisctrl.keys_del([self.redis_key, self.redis_dupefilter, self.redis_requests])