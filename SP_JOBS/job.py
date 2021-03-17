#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time : 2019/4/4 10:42
# @Author : way
# @Site : all
# @Describe: 基础类

import json
import logging
import random
import subprocess
from concurrent.futures import ThreadPoolExecutor
from SP.utils.base import ScheduledRequest
from SP.utils.ctrl_redis import RedisCtrl
from SP.utils.ctrl_ssh import SSH
from SP.settings import CLUSTER_ENABLE, SLAVES, SLAVES_BALANCE, SLAVES_ENV, SLAVES_WORKSPACE

logger = logging.getLogger("spiderman")
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s [%(name)s] %(levelname)s: %(message)s', "%Y-%m-%d %H:%M:%S")
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
ch.setFormatter(formatter)
logger.addHandler(ch)


class Job:

    @classmethod
    def push(cls, func):
        """
        :param func:
        :return: 将请求、定制headers 推到 redis
        """

        def wrapper(self, *args, **kwargs):
            reqs = func(self, *args, **kwargs)
            self.redisctrl.reqs_push(self.redis_key, reqs)
            if self.headers:
                self.redisctrl.add_string(self.redis_headers, json.dumps(self.headers, ensure_ascii=False))
            if self.cookies:
                self.redisctrl.add_set(self.redis_cookies, *self.cookies)

        return wrapper


class SPJob(Job):

    def __init__(self, spider_name):
        self.spider_name = spider_name
        self.redis_key = f'{spider_name}:start_urls'
        self.redis_dupefilter = f'{spider_name}:dupefilter'
        self.redis_requests = f'{spider_name}:requests'
        self.redis_headers = f'headers:{spider_name}'
        self.redis_cookies = f'cookies:{spider_name}'
        self.headers = None
        self.cookies = None
        self.redisctrl = RedisCtrl()

    # 生成任务，重写该函数
    @Job.push
    def make_job(self, pages):
        for pagenum in range(1, pages + 1):
            yield ScheduledRequest(
                url='',  # 请求地址
                method='',  # 请求方式  GET/POST
                callback='',  # 回调函数标识
                body={},  # post表单
                meta={}  # 元数据和反爬配置
            )

    # 删除redis上一次残留任务
    def delete(self):
        self.redisctrl.keys_del([self.redis_key, self.redis_dupefilter, self.redis_requests])

    # cluster模式下：ssh 启动slave爬虫
    def ssh_run(self, *args):
        slave = random.sample(SLAVES, 1)[0] if not SLAVES_BALANCE else SLAVES_BALANCE
        if SLAVES_ENV:
            cmd = f'source {SLAVES_ENV}/bin/activate; cd {SLAVES_WORKSPACE}; scrapy crawl {self.spider_name};'
        else:
            cmd = f"cd {SLAVES_WORKSPACE}; scrapy crawl {self.spider_name};"
        ssh = SSH(slave)
        hostname = ssh.hostname
        logger.info(f"slave:{hostname} 爬虫正在采集...")
        status, msg_out, msg_error = ssh.execute(cmd)
        if status != 0:
            logger.error(f"slave:{hostname} 爬虫执行失败：{msg_out + msg_error}")
        else:
            logger.info(f"slave:{hostname} 爬虫执行成功")

    # standalone模式下：启动爬虫
    def run(self, *args):
        cmd = f"scrapy crawl {self.spider_name}"
        logger.info(f"爬虫正在采集...")
        p = subprocess.Popen(cmd, shell=True)
        p.communicate()
        stdout, stderr = p.communicate()  # 忽视输出
        if p.returncode != 0:
            logger.error(f"爬虫执行失败：{stdout.decode('utf-8')} {stderr.decode('utf-8')}")
        else:
            logger.info(f"爬虫执行成功")

    # 执行爬虫
    def crawl(self, num=1):
        size = self.redisctrl.key_len(self.redis_key)

        if not size:
            logger.info(f"{self.redis_key} 中没有待执行的任务, 请检查！")
            return

        if CLUSTER_ENABLE:
            logger.name = "spiderman.model.cluster"
            if not (SLAVES or SLAVES_BALANCE):
                logger.error(f"请配置 SLAVES 机器！")
                return
            logger.info(f"初始任务数: {size} 启动爬虫数量: {num}")
            pool = ThreadPoolExecutor(max_workers=num)
            for _ in pool.map(self.ssh_run, range(num)):
                ...  # 等待所有线程完成
        else:
            logger.name = "spiderman.model.standalone"
            logger.info(f"初始任务数: {size} 启动爬虫数量: {num}")
            pool = ThreadPoolExecutor(max_workers=num)
            for _ in pool.map(self.run, range(num)):
                ...  # 等待所有线程完成
