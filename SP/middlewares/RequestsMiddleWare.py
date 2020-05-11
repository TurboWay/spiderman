#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time : 2019/6/20 17:46
# @Author : way
# @Site : 通用
# @Describe: 有时scrapy请求总是有问题，可以试试换成 requests 请求

import requests
from scrapy.http import HtmlResponse


class RequestMiddleWare(object):

    def __init__(self, encoding):
        self.encoding = encoding

    @classmethod
    def from_crawler(cls, crawler):
        settings = crawler.settings
        encoding = settings.get('encoding', 'utf-8')  # 设置解析编码编码，优先级1.cmd命令参数 2.spider.customer_data 3.setting，默认为utf-8
        return cls(encoding)

    def process_request(self, request, spider):
        headers = {key.decode('utf-8'): value[0].decode('utf-8') for key, value in request.headers.items()}
        if request.method == 'POST':
            response = requests.post(url=request.url, data=request.body, headers=headers)
        else:
            response = requests.get(url=request.url, headers=headers)
        return HtmlResponse(url=request.url, body=response.content, request=request, encoding=self.encoding,
                            status=response.status_code)
