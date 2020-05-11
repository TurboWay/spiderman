#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time : 2019/7/16 10:58
# @Author : way
# @Site : 通用
# @Describe: 使用cookies

class MiddleWare(object):

    def process_request(self, request, spider):
        cookies = request.meta.get('cookies')
        if cookies:
            request.cookies = cookies