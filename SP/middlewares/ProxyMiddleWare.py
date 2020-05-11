#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time : 2019/9/24 15:45
# @Author : way
# @Site : 通用
# @Describe: 使用代理ip


class ProxyMiddleWare(object):

    # 使用代理ip
    def process_request(self, request, spider):
        proxy = 'your proxy'
        proxies = {
            "http": f"http://{proxy}",
            "https": f"https://{proxy}",
        }
        tp = 'https' if request.url.startswith("https://") else 'http'
        request.meta['proxy'] = proxies.get(tp)