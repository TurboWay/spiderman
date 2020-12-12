#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time : 2019/6/20 17:46
# @Author : way
# @Site : 通用
# @Describe: payload 传参，需要特殊处理，可以直接使用该中间件

import requests, json, time
from scrapy.http import HtmlResponse

class MiddleWare(object):

    def __init__(self, **kwargs):
        self.encoding = kwargs.get('encoding', 'utf-8')
        self.time_out = kwargs.get('DOWNLOAD_TIMEOUT', 60)
        self.delay = kwargs.get('DOWNLOAD_DELAY', 0)

    @classmethod
    def from_crawler(cls, crawler):
        settings = crawler.settings
        return cls(**settings)

    def process_request(self, request, spider):
        if request.meta.get('payload'):
            headers = {key.decode('utf-8'): value[0].decode('utf-8') for key, value in request.headers.items()}
            payload = request.meta.get('payload')
            response = requests.post(url=request.url, data=json.dumps(payload), headers=headers, timeout=self.time_out)
            if self.delay > 0:
                time.sleep(self.delay)
            return HtmlResponse(url=request.url, body=response.content, request=request, encoding=self.encoding,
                                status=response.status_code)
