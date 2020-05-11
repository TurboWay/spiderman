#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time : 2019/11/4 14:52
# @Author : way
# @Site : 
# @Describe: 继承RetryMiddleware，增加response大小判断重试，可以应用于splash重新渲染 或者其它场景

from scrapy.downloadermiddlewares.retry import RetryMiddleware
from scrapy.utils.response import response_status_message

class MiddleWare(RetryMiddleware):

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