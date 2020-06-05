# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class SPItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


class SPfileItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    file_url = scrapy.Field({'idx': 1})  # 通用字段：附件链接
    file_type = scrapy.Field({'idx': 2})  # 通用字段：附件类型
    px = scrapy.Field({'idx': 3})  # 通用字段：文件序号
    file_name = scrapy.Field({'idx': 4})  # 通用字段：附件名称
    isload = scrapy.Field({'idx': 5, 'default': '未下载'})  # 通用字段：是否下载成功
    file_path = scrapy.Field({'idx': 6})  # 通用字段：附件本地存储路径
    fkey = scrapy.Field({'idx': 7})  # 通用字段：外键
    pagenum = scrapy.Field({'idx': 8})  # 通用字段：页码
