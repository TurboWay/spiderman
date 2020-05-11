#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time : 2019/7/16 17:08
# @Author : way
# @Site : 通用
# @Describe: 替换headers

class MiddleWare(object):

    def process_request(self, request, spider):
        headers = request.meta.get('headers')
        if headers:
            request.headers.update(headers)