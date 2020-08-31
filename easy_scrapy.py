#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time : 2019/3/14 13:39
# @Author : way
# @Site : 
# @Describe: 创建scrapy爬虫，自动生成文件到 相应的目录spiders , pipelines, items, GF_JOBS

import os
import time

item = """#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time : ${time}
# @Author : ${author}

from SP.items.items import *
from sqlalchemy.types import VARCHAR


class ${spidername}_list_Item(scrapy.Item):
    #  define table
    tablename = '${spidername}_list'
    tabledesc = '列表'
    # define the fields for your item here like:
    # 关系型数据库，可以自定义字段的类型、长度，默认 VARCHAR(length=255)
    # colname = scrapy.Field({'idx': 1, 'comment': '名称', 'type': VARCHAR(255)})
    
    
    # default column
    detail_full_url = scrapy.Field({'idx': 100, 'comment': '详情链接'})  # 通用字段
    pkey = scrapy.Field({'idx': 101, 'comment': 'md5(detail_full_url)'})  # 通用字段
    pagenum = scrapy.Field({'idx': 102, 'comment': '页码'})  # 通用字段


class ${spidername}_detail_Item(scrapy.Item):
    #  define table
    tablename = '${spidername}_detail'
    tabledesc = '详情'    
    # define the fields for your item here like:
    # 关系型数据库，可以自定义字段的类型、长度，默认 VARCHAR(length=255)
    # colname = scrapy.Field({'idx': 1, 'comment': '名称', 'type': VARCHAR(255)})
    
    
    # default column
    fkey = scrapy.Field({'idx': 100, 'comment': '等于list.pkey'})  # 通用字段
    pagenum = scrapy.Field({'idx': 101, 'comment': '页码'})  # 通用字段


class ${spidername}_file_Item(SPfileItem):
    #  define table
    tablename = '${spidername}_file'
    tabledesc = '附件'
"""


spider = """#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time : ${time}
# @Author : ${author}
# @Describe : ${describe}

from bs4 import BeautifulSoup
from SP.spiders.SPRedisSpider import SPRedisSpider
from SP.items.${spidername}_items import *
from SP.utils.make_jobs import ScheduledRequest, RedisCtrl
from SP.utils.make_key import md5
from SP.utils.make_log import log
from SP.utils.tool import get_file_type


class ${spidername}_Spider(SPRedisSpider):
    name = '${spidername}'
    redis_key = f'{name}:start_urls'
    allowed_domains = []
    custom_settings = {
        'LOG_LEVEL': "INFO",
        'LOG_FILE': log(name),
        # 'CONCURRENT_REQUESTS': 5,  # 控制并发数，默认16 
        # 'DOWNLOAD_DELAY': 3,  # 控制下载延迟，默认0
        'ITEM_PIPELINES': {
            # 'SP.pipelines.pipelines_file.FilePipeline': 100,    # 附件下载
            # 'SP.pipelines.pipelines_clean.CleanPipeline': 101,   # 字段清洗
            # 'SP.pipelines.pipelines_datafile.DataFilePipeline': 109,  # 写到数据文件
            'SP.pipelines.pipelines_rdbm.RdbmPipeline': 200,  # 关系型数据库
            # 'SP.pipelines.pipelines_hbase.HbasePipeline': 201,  # Hbase
            # 'SP.pipelines.pipelines_mongodb.MongodbPipeline': 202,  # Mongodb
            # 'SP.pipelines.pipelines_kafka.KafkaPipeline': 203,  # Kafka
            # 'SP.pipelines.pipelines_elasticsearch.ElasticSearchPipeline': 204,  # ElasticSearch
            # 'SP.pipelines.pipelines_hdfs.HdfsPipeline': 205  # hdfs, hive
        },
        'DOWNLOADER_MIDDLEWARES': {
            'SP.middlewares.UserAgentMiddleWare.UserAgentMiddleWare': 100,
            # 'SP.middlewares.HeadersMiddleWare.MiddleWare': 101,    # 在meta中增加headers
            # 'SP.middlewares.CookiesMiddleWare.MiddleWare': 102,    # 在meta中增加cookies
            # 'SP.middlewares.PayloadMiddleWare.MiddleWare': 103,    # 在meta中增加payload
            # 'SP.middlewares.ProxyMiddleWare.ProxyMiddleWare': 104,  # 使用代理ip
            # 'SP.middlewares.RequestsMiddleWare.RequestMiddleWare': 105,  # 使用requests
            # 'scrapy_splash.SplashCookiesMiddleware': 723,     # 在meta中增加splash 需要启用3个中间件
            # 'scrapy_splash.SplashMiddleware': 725,          # 在meta中增加splash 需要启用3个中间件
            # 'scrapy.downloadermiddlewares.httpcompression.HttpCompressionMiddleware': 810,    # 在meta中增加splash 需要启用3个中间件
            'SP.middlewares.SizeRetryMiddleware.MiddleWare': 900  # 重试中间件，允许设置 MINSIZE（int），response.body 长度小于该值时，自动触发重试
        },
    }

    def get_callback(self, callback):
        # url去重设置：True 不去重 False 去重
        callback_dt = {
            'list': (self.list_parse, True),
            'detail': (self.detail_parse, True),
        }
        return callback_dt.get(callback)

    def list_parse(self, response):
        rows = BeautifulSoup(response.text, 'lxml')
        reqs = []
        for row in rows:
            detail_url = row.find('a').get('href')
            list_item = ${spidername}_list_Item()
            # save value for your item here like:
            # list_item['title'] = row.find('a').text
            
            # default column
            list_item['detail_full_url'] = response.urljoin(detail_url)
            list_item['pkey'] = md5(list_item['detail_full_url'])
            list_item['pagenum'] = response.meta.get('pagenum')
            yield list_item

            req = ScheduledRequest(
                url=list_item['detail_full_url'],  
                method='GET',
                callback='detail',
                body={},  # 如果是POST，在这边填写post字典
                meta={
                    'fkey': list_item['pkey'],
                    'pagenum': list_item['pagenum'],
                    # 反爬相关的meta字典也填写这边，然后在spider中启用相应的中间件
                    # 'cookies': {},      # 一般反爬
                    # 'splash': {'wait': 2}  # js加载、异步加载渲染
                }
            )
            reqs.append(req)

        # 将详情链接作为新的任务 推到redis
        RedisCtrl().reqs_push(self.redis_key, reqs)

    def detail_parse(self, response):
        soup = BeautifulSoup(response.text, 'lxml')

        detail_item = ${spidername}_detail_Item()
        # save value for your item here like:
        # detail_item['title'] = soup.find('h1').text
        
        # default column
        detail_item['fkey'] = response.meta.get('fkey')
        detail_item['pagenum'] = response.meta.get('pagenum')
        yield detail_item
        
        file_item = ${spidername}_file_Item()
        file_url = soup.find('your xpath').get('href')
        # save value for your item here like:
        # file_item['file_url'] = response.urljoin(file_url)
        file_item['px'] = 1
        file_item['file_url'] = response.urljoin(file_url)
        file_item['file_name'] = ""
        file_item['file_type'] = get_file_type(file_url, 'jpg')
        # default column
        file_item['fkey'] = response.meta.get('fkey')
        file_item['pagenum'] = response.meta.get('pagenum')
        yield file_item
"""

job = """#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time : ${time}
# @Author : ${author}

import os
import sys
import getopt

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from SP_JOBS.job import *
from SP.spiders.${spidername} import ${spidername}_Spider


class ${spidername}_job(SPJob):

    def __init__(self):
        super().__init__(spider_name=${spidername}_Spider.name)
        self.delete()

    def make_job(self, pages):
        for pagenum in range(1, pages + 1):
            url = ''
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
    job = ${spidername}_job()
    job.make_job(pages)
    job.crawl(num)
"""

job_patch = """#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time : ${time}
# @Author : ${author}

import os
import sys
import getopt

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from SP_JOBS.job import *
from SP.spiders.${spidername} import ${spidername}_Spider
from SP.utils.tool import rdbm_execute


class ${spidername}_job(SPJob):

    def __init__(self):
        super().__init__(spider_name=${spidername}_Spider.name)
        self.delete()

    def make_list_job(self, pages):
        sql = \"\"\"
               select pagenum 
               from ${spidername}_list 
               group by pagenum 
                \"\"\"
        rows = rdbm_execute(sql)
        rows = [int(row[0]) for row in rows]
        ret = list(set(range(1, pages + 1)) - set(rows))  # 未采集的页码
        for pagenum in ret:
            url = ''
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
        sql = \"\"\"
                select a.detail_full_url, a.pagenum, a.pkey
                from ${spidername}_list a 
                left join ${spidername}_detail b on a.pkey = b.fkey
                where b.keyid is null
                \"\"\"
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
    job = ${spidername}_job()
    job.make_list_job(pages)    # list 补爬
    job.make_detail_job()       # detail 补爬
    job.crawl(num)
"""


def spider_info(spidername):
    info = {}
    info['spider_path'] = f'{os.getcwd()}\SP\spiders\{spidername}.py'
    info['item_path'] = f'{os.getcwd()}\SP\items\{spidername}_items.py'
    info['job_path'] = f'{os.getcwd()}\SP_JOBS\{spidername}_job.py'
    info['job_patch'] = f'{os.getcwd()}\SP_JOBS\{spidername}_job_patch.py'
    return info


def delete_spider(spidername):
    info = spider_info(spidername)
    for path in info.values():
        if os.path.exists(path):
            os.remove(path)
            print(f"{path} 删除成功")


def open_in_pycharm(job_path, pycharm):
    if not pycharm:
        return
    if os.path.exists(pycharm):
        cmd = f'"{pycharm}" {job_path}'
        os.system(cmd)
        return
    print("your pycharm not in utils.tool.open_in_pycharm, please add your PyCharm exe or link")


def new(**kwargs):
    """
    :param kwargs: 新增一个全新的爬虫
    :return:
    """
    spidername = kwargs.get('spidername')
    describe = kwargs.get('describe')
    author = kwargs.get('author')
    item = kwargs.get('item')
    spider = kwargs.get('spider')
    job = kwargs.get('job')
    pycharm = kwargs.get('pycharm')

    if not spidername:
        raise NameError("spidername不允许为空, 请检查！")

    info = spider_info(spidername)
    if os.path.exists(info['job_path']):
        print((f"{spidername}已存在！"))
        open_in_pycharm(info['job_path'], pycharm)  # 自动打开job文件
        return

    for path in info.values():
        if os.path.exists(path):
            raise NameError(f"{path}已存在, 请检查！")

    replace_map = {
        '${spidername}': spidername,
        '${describe}': describe,
        '${author}': author,
        '${time}': time.strftime("%Y-%m-%d %H:%M", time.localtime()),
    }

    for key, val in replace_map.items():
        item = item.replace(key, val)
        spider = spider.replace(key, val)
        job = job.replace(key, val)

    path_map = {
        info['spider_path']: spider,
        info['item_path']: item,
        info['job_path']: job
    }

    # 创建文件
    for path, st in path_map.items():
        with open(path, 'w', encoding='utf-8') as f:
            f.write(st)

    pathmsg = '\n'.join(path_map.keys())
    msg = f"爬虫创建成功，请前往调整修改:\n{pathmsg}"
    print(msg)
    open_in_pycharm(info['job_path'], pycharm)  # 自动打开job文件
    # open_in_pycharm(spider_path)  # 自动打开spider文件


def patch(**kwargs):
    """
        :param kwargs: 新增补爬job
        :return:
        """
    spidername = kwargs.get('spidername')
    author = kwargs.get('author')
    job_patch = kwargs.get('job_patch')
    pycharm = kwargs.get('pycharm')

    if not spidername:
        raise NameError("spidername不允许为空, 请检查！")

    job_path = f'{os.getcwd()}\SP_JOBS\{spidername}_job_patch.py'
    if os.path.exists(job_path):
        print(f"{job_path}已存在!")
        open_in_pycharm(job_path, pycharm)  # 自动打开job文件
        return

    replace_map = {
        '${spidername}': spidername,
        '${author}': author,
        '${time}': time.strftime("%Y-%m-%d %H:%M", time.localtime()),
    }

    # 创建文件
    with open(job_path, 'w', encoding='utf-8') as f:
        for key, val in replace_map.items():
            job_patch = job_patch.replace(key, val)
        f.write(job_patch)

    msg = f"补爬job创建成功，请前往调整修改：{job_path}"
    print(msg)
    open_in_pycharm(job_path, pycharm)  # 自动打开job文件
    # open_in_pycharm(spider_path)  # 自动打开spider文件


if __name__ == "__main__":
    # 【必填】爬虫名称
    spidername = ''

    # 【可选】爬虫简单描述
    describe = ''

    # 是否生成补爬job_patch文件, 默认 False
    make_job_patch = False

    # 删除爬虫的所有代码文件，有时候可能名字没取好，强迫症。。。
    # delete_spider(spidername)

    # 个人配置
    author = 'way'
    pycharm = r"C:\Users\Public\Desktop\PyCharm Community Edition 2019.3.1 x64.lnk"

    # 若爬虫已存在，则打开对应job文件；若不存在，则自动创建并打开对应job文件
    # ---------------------------------------------------------- # 新建爬虫
    new(
        spidername=spidername,
        describe=describe,
        author=author,
        item=item,
        spider=spider,
        job=job,
        pycharm=pycharm,
    )

    # ---------------------------------------------------------- # 新建补爬job
    if make_job_patch:
        patch(
            spidername=spidername,
            author=author,
            job_patch=job_patch,
            pycharm=pycharm,
        )
