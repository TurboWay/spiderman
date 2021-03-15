#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time : 2020-05-09 15:31
# @Author : way

import os
import sys
import getopt

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from SP_JOBS.job import *
from SP.spiders.zhifang import zhifang_Spider


class zhifang_job(SPJob):

    def __init__(self):
        super().__init__(spider_name=zhifang_Spider.name)
        self.delete()  # 如需去重、增量采集，请注释该行
        self.headers = {
            # 有反爬的话，可以在这边定制请求头
        }

    @Job.push
    def make_job(self, pages):
        for pagenum in range(1, pages + 1):
            url = f'https://esf.zhifang.com/dq00000/{pagenum}'
            yield ScheduledRequest(
                url=url,  # 请求地址
                method='GET',  # 请求方式  GET/POST
                callback='list',  # 回调函数标识
                body={},  # 如果是POST，在这边填写post字典
                meta={
                    'pagenum': pagenum,  # 页码
                    # 'payload': {},      # request payload 传输方式
                    # 'splash' : {'wait': 2}  # js加载、异步加载渲染
                }
            )


if __name__ == "__main__":
    # 采集页数
    pages = 10
    # 爬虫数量
    num = 2

    # 支持传参调用
    opts, args = getopt.getopt(sys.argv[1:], "p:n:", ["pages=", "num="])
    for op, value in opts:
        if op in ("-p", "--pages"):
            pages = int(value)
        elif op in ("-n", "--num"):
            num = int(value)

    # 执行采集
    job = zhifang_job()
    job.make_job(pages)
    job.crawl(num)
