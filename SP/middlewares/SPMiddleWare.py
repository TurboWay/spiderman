#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time : 2021/3/14 20:41
# @Author : way
# @Site : 
# @Describe: 各种反爬虫中间件

import time
import json
import random
import requests
from scrapy.http import HtmlResponse
from scrapy.downloadermiddlewares.retry import RetryMiddleware
from scrapy.utils.response import response_status_message
from SP.utils.ctrl_redis import RedisCtrl

USER_AGENT_LIST = (
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1",
    "Mozilla/5.0 (X11; CrOS i686 2268.111.0) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.57 Safari/536.11",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1092.0 Safari/536.6",
    "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1090.0 Safari/536.6",
    "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/19.77.34.5 Safari/537.1",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.9 Safari/536.5",
    "Mozilla/5.0 (Windows NT 6.0) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.36 Safari/536.5",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
    "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Trident/4.0; SE 2.X MetaSr 1.0; SE 2.X MetaSr 1.0; .NET CLR 2.0.50727; SE 2.X MetaSr 1.0)",
    "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; 360SE)",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
    "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
    "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.0 Safari/536.3",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24",
    "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24"
)


class UserAgentMiddleWare(object):
    """
    随机 user-agent
    """

    def process_request(self, request, spider):
        request.headers["User-Agent"] = random.choice(USER_AGENT_LIST)


class HeadersMiddleWare(object):
    """
    定制请求头
    """

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.spider.name)

    def __init__(self, name):
        self.headers = RedisCtrl().get_string(f'headers:{name}')
        self.headers = eval(self.headers)

    def process_request(self, request, spider):
        request.headers.update(self.headers)


class ProxyMiddleWare(object):
    """
    代理 ip 中间件
    """

    def process_request(self, request, spider):
        proxy = 'your proxy'
        proxies = {
            "http": f"http://{proxy}",
            "https": f"https://{proxy}",
        }
        tp = 'https' if request.url.startswith("https://") else 'http'
        request.meta['proxy'] = proxies.get(tp)


class SizeRetryMiddleWare(RetryMiddleware):
    """
    继承RetryMiddleware，增加response大小判断重试，可以应用于splash重新渲染 或者其它场景
    """

    def __init__(self, settings):
        super().__init__(settings)
        self.minsize = settings.get('MINSIZE')

    def process_response(self, request, response, spider):
        if request.meta.get('dont_retry', False):
            return response
        if response.status in self.retry_http_codes:
            reason = response_status_message(response.status)
            return self._retry(request, reason, spider) or response
        if self.minsize and len(response.body) < self.minsize:
            return self._retry(request, f"响应长度小于{self.minsize}", spider) or response
        return response

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.settings)


class RequestsMiddleWare(object):
    """
    有时scrapy请求总是有问题，可以试试换成 requests 请求
    """

    def __init__(self, **kwargs):
        self.encoding = kwargs.get('ENCODING', 'utf-8')
        self.time_out = kwargs.get('DOWNLOAD_TIMEOUT', 60)
        self.delay = kwargs.get('DOWNLOAD_DELAY', 0)

    @classmethod
    def from_crawler(cls, crawler):
        settings = crawler.settings
        return cls(**settings)

    def process_request(self, request, spider):
        headers = {key.decode('utf-8'): value[0].decode('utf-8') for key, value in request.headers.items()}
        if request.meta.get('payload'):
            response = requests.post(url=request.url, data=json.dumps(request.meta.get('payload')), headers=headers, timeout=self.time_out)
        elif request.method == 'POST':
            response = requests.post(url=request.url, data=request.body, headers=headers, timeout=self.time_out)
        else:
            response = requests.get(url=request.url, headers=headers, timeout=self.time_out)
        if self.delay > 0:
            time.sleep(self.delay)
        return HtmlResponse(url=request.url, body=response.content, request=request, encoding=self.encoding,
                            status=response.status_code)
