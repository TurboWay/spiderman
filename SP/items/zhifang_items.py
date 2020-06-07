#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time : 2020-05-09 15:31
# @Author : way

from SP.items.items import *
from sqlalchemy.types import VARCHAR


class zhifang_list_Item(scrapy.Item):  # 列表页
    #  define the tablename
    tablename = 'zhifang_list'
    # define the fields for your item here like:
    # 关系型数据库，可以自定义字段的类型、长度，默认 VARCHAR(length=255)
    # colname = scrapy.Field({'idx': 1, 'comment': '名称', type: VARCHAR(255)})
    tit = scrapy.Field({'idx': 1, 'comment': '房屋标题'})
    txt = scrapy.Field({'idx': 2, 'comment': '房屋描述'})
    tit2 = scrapy.Field({'idx': 3, 'comment': '房屋楼层'})
    price = scrapy.Field({'idx': 4, 'comment': '房屋价格'})
    agent = scrapy.Field({'idx': 5, 'comment': '房屋中介'})
    # default column
    detail_full_url = scrapy.Field({'idx': 100, 'comment': '详情链接'})  # 通用字段
    pkey = scrapy.Field({'idx': 101, 'comment': 'md5(detail_full_url)'})  # 通用字段
    pagenum = scrapy.Field({'idx': 102, 'comment': '页码'})  # 通用字段


class zhifang_detail_Item(scrapy.Item):  # 详情页
    #  define the tablename
    tablename = 'zhifang_detail'
    # define the fields for your item here like:
    # 关系型数据库，可以自定义字段的类型、长度，默认 VARCHAR(length=255)
    # colname = scrapy.Field({'idx': 1, 'comment': '名称', type: VARCHAR(255)})
    type1 = scrapy.Field({'idx': 1, 'comment': '户型楼层'})
    type2 = scrapy.Field({'idx': 2, 'comment': '朝向类型'})
    type3 = scrapy.Field({'idx': 3, 'comment': '面积结构'})
    plot_name = scrapy.Field({'idx': 4, 'comment': '小区名称'})
    area = scrapy.Field({'idx': 5, 'comment': '所在区域'})
    look_time = scrapy.Field({'idx': 6, 'comment': '看房时间'})
    source_id = scrapy.Field({'idx': 7, 'comment': '房源标号'})
    # default column
    fkey = scrapy.Field({'idx': 100, 'comment': '等于list.pkey'})  # 通用字段
    pagenum = scrapy.Field({'idx': 101, 'comment': '页码'})  # 通用字段


class zhifang_file_Item(SPfileItem):  # 附件表
    #  define the tablename
    tablename = 'zhifang_file'
    pass
