#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time : 2021/3/17 21:51
# @Author : way
# @Site : 
# @Describe: api 服务 未完成

import os
import time
import uuid
import subprocess
import socket
import uvicorn
from fastapi import FastAPI

app = FastAPI()

Host = socket.gethostbyname(socket.gethostname())


class Task:
    def __init__(self, **kwargs):
        self.id = uuid.uuid1()
        self.spider = kwargs.get('spider')
        self.cmd = kwargs.get('cmd')
        self.pid = kwargs.get('pid')
        self.host = Host
        self.start = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())


# 获取所有的爬虫名字
@app.get("/openapi/spiders")
async def spiders():
    spiders = []
    for file in os.listdir('SP/spiders'):
        if file not in ('__init__.py', 'SPRedisSpider.py', '__pycache__'):
            spiders.append(file.split('.')[0])
    return {'total': len(spiders), 'spiders': spiders}


# 查看所有正在运行的爬虫进程

# 启动爬虫任务

# 启动爬虫
@app.get("/openapi/run/{spider}")
async def run(spider: str):
    task = Task()
    task.spider = spider
    task.cmd = f'scrapy crawl {spider}'
    p = subprocess.Popen(task.cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    task.pid = p.pid
    # task push 到 redis
    stdout, stderr = p.communicate()
    # redis task remove
    end = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
    return {'returncode': p.returncode, 'host': task.host, 'cmd': task.cmd, 'start': task.start, 'end': end,
            'stderr': stderr, 'stdout': stdout}


# 停止爬虫进程

# 停止单个爬虫

# 停止所有爬虫

if __name__ == '__main__':
    uvicorn.run(app='api:app', host="127.0.0.1", port=2021, reload=True)
