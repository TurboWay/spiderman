#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time : 2019/3/5 15:31
# @Author : XXX
# @Site : 
# @Describe: 生成各种key

import hashlib
import time
import uuid

bizdate = time.strftime('%Y%m%d', time.localtime())


def md5(id):
    key = hashlib.md5(str(id).encode(encoding='utf-8')).hexdigest()
    return key.upper()


def rowkey():
    content = str(uuid.uuid1()).replace('-', '').upper()
    key = f'{bizdate}_{content}'
    return key

