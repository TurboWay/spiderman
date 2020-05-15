#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time : 2020-05-09 15:31
# @Author : way

from SP.items.items import *


class zhifang_list_Item(scrapy.Item):  # 列表页
    # define the fields for your item here like:
    # name = scrapy.Field()  # comment
    tit = scrapy.Field()  # 房屋标题
    txt = scrapy.Field()  # 房屋描述
    tit2 = scrapy.Field()  # 房屋楼层
    price = scrapy.Field()  # 房屋价格
    agent = scrapy.Field()  # 房屋中介
    # default column
    detail_full_url = scrapy.Field()  # 通用字段：详情链接
    pkey = scrapy.Field()  # 通用字段：md5(detail_full_url)
    pagenum = scrapy.Field()  # 通用字段：页码


class zhifang_detail_Item(scrapy.Item):  # 详情页
    # define the fields for your item here like:
    # name = scrapy.Field() # comment
    type1 = scrapy.Field()  # 户型楼层
    type2 = scrapy.Field()  # 朝向类型
    type3 = scrapy.Field()  # 面积结构
    plot_name = scrapy.Field()  # 小区名称
    area = scrapy.Field()  # 所在区域
    look_time = scrapy.Field()  # 看房时间
    source_id = scrapy.Field()  # 房源标号
    # default column
    fkey = scrapy.Field()  # 通用字段：等于list.pkey
    pagenum = scrapy.Field()  # 通用字段：页码


class zhifang_file_Item(SPfileItem):  # 附件表
    pass
