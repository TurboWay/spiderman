#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time : 2021/3/16 19:11
# @Author : way
# @Site : 
# @Describe: 附件下载器

import os
import time
import random
import json
import logging
import requests
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor
from SP.utils.base import md5, ScheduledRequest, bizdate as BIZDATE
from SP.utils.ctrl_redis import RedisCtrl
from SP.utils.tool import rdbm_session
from SP_JOBS.job import Job
from SP.settings import FILES_STORE

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s [%(name)s] %(levelname)s: %(message)s', "%Y-%m-%d %H:%M:%S")
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
ch.setFormatter(formatter)
logger.addHandler(ch)


class DownLoad(Job):

    def __init__(self, **kwargs):
        """
        :param kwargs:
        """
        self.spider = kwargs.get('spider')
        self.redis_key = f'file:{self.spider}'
        self.table = f'{self.spider}_file'
        self.bizdate = kwargs.get('bizdate', BIZDATE)
        self.dir = kwargs.get('dir', FILES_STORE)
        self.retry = kwargs.get('retry', 3)
        self.delay = kwargs.get('delay', 0)
        self.max_workers = kwargs.get('max_workers', 10)
        self.overwrite = kwargs.get('overwrite', False)
        self.batch = self.max_workers * 2
        self.redisctrl = RedisCtrl()
        self.headers = None
        self.cookies = None

    @Job.push
    def make_job(self):
        """
        :return: 读取附件表的元数据，生成请求推到 redis
        """
        sql = f"select keyid, file_url, file_type, file_name from {self.table} where bizdate >= '{self.bizdate}' and status in ('未下载', '下载失败') "
        with rdbm_session() as session:
            for row in session.execute(sql).fetchall():
                keyid, file_url, file_type, file_name = row
                yield ScheduledRequest(
                    url=file_url,  # 请求地址
                    method='GET',  # 请求方式  GET/POST
                    body={},  # post表单
                    meta={'keyid': keyid, 'file_type': file_type, 'file_name': file_name}  # 元数据
                )

    def delete(self):
        """
        :return: 删除 redis key
        """
        return self.redisctrl.keys_del([self.redis_key])

    def get_reqs(self):
        """
        :return: 从 redis 获取附件下载请求
        """
        return self.redisctrl.pop_list(self.redis_key, self.batch)

    def get_job_size(self):
        """
        :return: 获取所有的请求数量
        """
        return self.redisctrl.key_len(self.redis_key)

    def get_file_path(self, file_url, file_type, file_name):
        """
        :param file_url:
        :param file_type:
        :return: 附件路径
        """
        if not file_name:
            file_name = md5(file_url) + '.' + file_type
        return self.dir + '/' + self.spider + '/' + file_name

    def file_path_check(self, file_path):
        """
        :param file_path:
        :return: 检查附件是否存在
        """
        if not os.path.exists(file_path):
            try:
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
            except FileExistsError:
                ...
        return os.path.exists(file_path)

    def file_download(self, req):
        """
        :param req:
        :return: 下载附件
        """
        scheduled = ScheduledRequest(**json.loads(req))
        file_url = scheduled.url
        keyid = scheduled.meta.get('keyid')
        file_type = scheduled.meta.get('file_type')
        file_name = scheduled.meta.get('file_name')
        file_path = self.get_file_path(file_url, file_type, file_name)
        status = '下载成功'
        if not self.file_path_check(file_path) or self.overwrite:
            retry = 1
            while retry <= self.retry:
                try:
                    if self.cookies:
                        self.headers['Cookie'] = random.choice(self.cookies)
                    with requests.session() as session:
                        session.keep_alive = False
                        if scheduled.method == 'POST':
                            res = session.post(file_url, headers=self.headers, data=scheduled.body, stream=True,
                                               timeout=60)
                        else:
                            res = session.get(file_url, headers=self.headers, stream=True, timeout=60)
                        if res.status_code not in [200]:
                            raise Exception(f"请求失败，状态码：{res.status_code}")  # 响应不是200 则认为失败
                        with open(file_path, 'wb') as f:
                            for chunk in res.iter_content(chunk_size=512):
                                f.write(chunk)
                        status = '下载成功'
                        break
                except Exception as e:
                    status = '下载失败'
                    logger.warning(f"{file_url}第{retry}次下载失败：{e}")
                finally:
                    retry += 1
                    if self.delay > 0:
                        time.sleep(self.delay)
        return keyid, file_path, status

    def file_meta_update(self, results):
        """
        :param results:
        :return: 更新附件表的元数据
        """
        with rdbm_session() as session:
            for result in results:
                keyid, file_path, status = result
                sql = f"update {self.table} set file_path='{file_path}', status='{status}' where keyid = '{keyid}'; "
                session.execute(sql)
            session.commit()

    def run(self):
        """
        :return: 并发下载附件
        """
        self.headers = self.redisctrl.get_string(f'headers:{self.spider}')
        self.cookies = self.redisctrl.get_string(f'cookies:{self.spider}')
        total = self.get_job_size()
        results = []
        while True:
            remain = self.get_job_size()
            with tqdm(total=total, desc='下载中...') as pbar:
                if pbar.total - remain > pbar.last_print_n:
                    pbar.update(pbar.total - remain)
                if remain > 0:
                    reqs = self.get_reqs()
                    with ThreadPoolExecutor(max_workers=self.max_workers) as pool:
                        for result in pool.map(self.file_download, reqs):
                            pbar.update(1)
                            results.append(result)
                            if len(results) >= 100:
                                self.file_meta_update(results)
                                results.clear()
            if remain == 0:
                if len(results) > 0:
                    self.file_meta_update(results)
                logger.info("全部下载完成")
                break

# if __name__ == '__main__':
#     dw = DownLoad(spider='zhifang')
#     dw.make_job()
#     dw.run()
