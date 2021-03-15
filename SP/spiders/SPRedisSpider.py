#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time : 2019/4/8 10:44
# @Author : way
# @Site : all
# @Describe: 基础类, 从redis读取请求数据，构造成scrapy请求

import json
from scrapy_redis.spiders import RedisSpider, bytes_to_str
from SP.utils.base import ScheduledRequest
from scrapy.http import Request, FormRequest
from scrapy_splash import SplashRequest, SplashFormRequest


class SPRedisSpider(RedisSpider):

    def get_callback(self, callback):
        """
        :param callback:
        :return: 继承时重写该函数，返回一个元组(func, bool)
        """
        return None, False

    def make_request_from_data(self, data):
        """
        :param data: redis_key中的数据
        :return: 生成 scrapy请求
        """
        scheduled = ScheduledRequest(
            **json.loads(
                bytes_to_str(data, self.redis_encoding)
            )
        )

        callback, dont_filter = self.get_callback(scheduled.callback)
        if not callable(callback):
            raise OSError(f"{scheduled.callback}没有指定回调函数")

        params = {
            'url': scheduled.url,
            'method': scheduled.method,
            'meta': scheduled.meta,
            'dont_filter': dont_filter,
            'callback': callback
        }

        if 'splash' in scheduled.meta:
            wait = scheduled.meta.get('splash').get('wait', 2)
            images = scheduled.meta.get('splash').get('images', 0)  # 默认不下载图片
            params['args'] = {'wait': wait, 'images': images}
            if scheduled.method == "POST":
                return SplashFormRequest(formdata=scheduled.body, **params)
            else:
                return SplashRequest(**params)

        if scheduled.method == "POST":
            return FormRequest(formdata=scheduled.body, **params)
        else:
            return Request(**params)
