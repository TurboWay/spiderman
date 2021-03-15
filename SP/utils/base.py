#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time : 2021/3/15 20:50
# @Author : way
# @Site : 
# @Describe: 基础类、方法

import os
import time
import uuid
import hashlib
from SP.settings import LOGDIR

bizdate = time.strftime('%Y%m%d', time.localtime())


# scrapy_redis请求类
class ScheduledRequest:

    def __init__(self, **kwargs):
        self.url = kwargs.get('url')
        self.method = kwargs.get('method', 'GET')
        self.callback = kwargs.get('callback')
        self.body = kwargs.get('body')
        self.meta = kwargs.get('meta')


def log(name):
    # 生成日志文件夹
    logpath = f'{LOGDIR}/{bizdate}'
    os.makedirs(logpath, exist_ok=True)

    # 生成日志路径
    logfile = f'{logpath}/{name}.log'
    return logfile


def md5(id):
    key = hashlib.md5(str(id).encode(encoding='utf-8')).hexdigest()
    return key.upper()


def rowkey():
    content = str(uuid.uuid1()).replace('-', '').upper()
    key = f'{bizdate}_{content}'
    return key
