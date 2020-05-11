#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time : 2020-05-09 15:31
# @Author : way

from SP.items.items import *


class zhifang_list_Item(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    tit = scrapy.Field()
    txt = scrapy.Field()
    tit2 = scrapy.Field()
    price = scrapy.Field()
    agent = scrapy.Field()
    # default column
    detail_full_url = scrapy.Field()  # 通用字段：详情链接
    pkey = scrapy.Field()  # 通用字段：md5(detail_full_url)
    pagenum = scrapy.Field()  # 通用字段：页码


class zhifang_detail_Item(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    type1 = scrapy.Field()
    type2 = scrapy.Field()
    type3 = scrapy.Field()
    plot_name = scrapy.Field()
    area = scrapy.Field()
    look_time = scrapy.Field()
    source_id = scrapy.Field()
    # default column
    fkey = scrapy.Field()  # 通用字段：等于list.pkey
    pagenum = scrapy.Field()  # 通用字段：页码


class zhifang_file_Item(SPfileItem):
    pass