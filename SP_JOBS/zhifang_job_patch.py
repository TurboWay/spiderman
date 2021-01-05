#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time : 2020-05-14 13:50
# @Author : way

import os
import sys
import getopt

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from SP_JOBS.job import *
from SP.spiders.zhifang import zhifang_Spider
from SP.utils.tool import rdbm_execute


class zhifang_job(SPJob):

    def __init__(self):
        super().__init__(spider_name=zhifang_Spider.name)
        self.delete()  # 如需去重、增量采集，请注释该行

    def make_list_job(self, pages):
        sql = """
               select pagenum 
               from zhifang_list 
               group by pagenum 
                """
        rows = rdbm_execute(sql)
        rows = [int(row[0]) for row in rows]
        ret = list(set(range(1, pages + 1)) - set(rows))  # 未采集的页码
        for pagenum in ret:
            url = f'https://esf.zhifang.com/dq00000/{pagenum}'
            req = ScheduledRequest(
                url=url,  # 请求地址
                method='GET',  # 请求方式  GET/POST
                callback='list',  # 回调函数标识
                body={},  # 如果是POST，在这边填写post字典
                meta={
                    'pagenum': pagenum,  # 页码
                    # 反爬相关的meta字典也填写这边，然后在spider中启用相应的中间件
                    # 'headers': {},      # 一般反爬
                    # 'cookies': {},      # 一般反爬
                    # 'payload': {},      # request payload 传输方式
                    # 'splash': {'wait': 2}  # js加载、异步加载渲染
                }
            )
            self.reqs.append(req)
        self.push()

    def make_detail_job(self):
        sql = """
                select a.detail_full_url, a.pagenum, a.pkey
                from zhifang_list a 
                left join zhifang_detail b on a.pkey = b.fkey
                where b.keyid is null
                """
        rows = rdbm_execute(sql)
        for row in rows:
            detail_full_url, pagenum, pkey = row
            req = ScheduledRequest(
                url=detail_full_url,  
                method='GET',
                callback='detail',
                body={},       # 如果是POST，在这边填写post字典
                meta={
                    'pagenum': pagenum,  # 页码
                    'fkey': pkey,  # 外键
                    # 反爬相关的meta字典也填写这边，然后在spider中启用相应的中间件
                    # 'headers': {},      # 一般反爬
                    # 'cookies': {},      # 一般反爬
                    # 'payload': {},      # request payload 传输方式
                    # 'splash': {'wait': 2}  # js加载、异步加载渲染
                }
                )
            self.reqs.append(req)
        self.push()
        
        
if __name__ == "__main__":
    # 采集页数
    pages = 1
    # 爬虫数量
    num = 1

    # 支持传参调用
    opts, args = getopt.getopt(sys.argv[1:], "p:n:", ["pages=", "num="])
    for op, value in opts:
        if op in ("-p", "--pages"):
            pages = int(value)
        elif op in ("-n", "--num"):
            num = int(value)

    # 执行采集
    job = zhifang_job()
    job.make_list_job(pages)    # list 补爬
    job.make_detail_job()       # detail 补爬
    job.crawl(num)
