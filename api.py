#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time : 2021/3/17 21:51
# @Author : way
# @Site : 
# @Describe: api 服务

import os
import time
import json
import psutil
import subprocess
import socket
import uvicorn
from uuid import uuid1
from fastapi import FastAPI
from typing import Optional
from SP.utils.ctrl_redis import RedisCtrl

app = FastAPI()

Host = socket.gethostbyname(socket.gethostname())


class Task:
    def __init__(self, **kwargs):
        self.id = kwargs.get('id')
        self.spider = kwargs.get('spider')
        self.cmd = kwargs.get('cmd')
        self.pid = kwargs.get('pid')
        self.host = Host
        self.start = kwargs.get('start', time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()))


class TaskRedis:
    def __init__(self):
        self.redis_key = 'tasks'
        self.redisctrl = RedisCtrl()

    def push(self, task):
        val = json.dumps(task.__dict__, ensure_ascii=False)
        self.redisctrl.add_hash(self.redis_key, task.id, val)

    def remove(self, id):
        self.redisctrl.remove_hash(self.redis_key, id)

    def get_task(self, id):
        return self.redisctrl.get_hash(self.redis_key, id)

    def get_tasks(self, spider=None, sort='spider'):
        tasks_map = {}
        for val in self.redisctrl.get_hashall(self.redis_key).values():
            task = Task(**json.loads(val))
            if spider and spider != task.spider:
                continue
            sort_key = task.host if sort == 'host' else task.spider
            tasks = tasks_map.get(sort_key, [])
            tasks.append(task.__dict__)
            tasks_map[sort_key] = tasks
        return tasks_map


# 获取所有的爬虫名字
@app.get("/openapi/spiders")
async def spiders():
    spiders = []
    for file in os.listdir('SP/spiders'):
        if file not in ('__init__.py', 'SPRedisSpider.py', '__pycache__'):
            spiders.append(file.split('.')[0])
    return {'total': len(spiders), 'spiders': spiders}


# 查看所有正在运行的爬虫进程
@app.get("/openapi/tasks")
async def tasks(spider: Optional[str] = None, sort: Optional[str] = 'spider'):
    tasks = TaskRedis().get_tasks(spider, sort)
    return {'total': len(tasks), 'tasks': tasks}


# 启动爬虫 job or run
@app.get("/openapi/run/{spider}")
def run(spider: str, type: Optional[str] = None, pages: Optional[int] = None):
    task = Task()
    task.spider = spider
    if type == 'job':
        task.cmd = f'python SP_JOBS/{spider}_job.py --onlyjob true'
        if pages:
            task.cmd += f' -p {pages}'
    elif type == 'job_patch':
        task.cmd = f'python SP_JOBS/{spider}_job_patch.py --onlyjob true'
        if pages:
            task.cmd += f' -p {pages}'
    else:
        task.cmd = f'scrapy crawl {spider}'
    p = subprocess.Popen(task.cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    task.pid = p.pid
    task.id = str(uuid1())
    redis = TaskRedis()
    redis.push(task)
    stdout, stderr = p.communicate()
    redis.remove(task.id)
    msg = stdout.decode('gbk') + stderr.decode('gbk')
    end = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
    return {'returncode': p.returncode, 'host': task.host, 'cmd': task.cmd, 'start': task.start, 'end': end, 'msg': msg}


# 停止爬虫进程
@app.get("/openapi/kill/{id}")
def kill(id: str):
    redis = TaskRedis()
    task = redis.get_task(id)
    task = Task(**json.loads(task))
    if task.host != Host:
        return {'returncode': -1, 'msg': '非本机进程'}
    else:
        try:
            p = psutil.Process(task.pid)
            for son in p.children(recursive=True):
                son.terminate()
            p.terminate()
        except Exception as e:
            return {'returncode': -1, 'msg': str(e)}
        redis.remove(task.id)
        return {'returncode': 0, 'msg': 'success'}


if __name__ == '__main__':
    uvicorn.run(app='api:app', host="127.0.0.1", port=2021, reload=True)
