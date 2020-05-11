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
    file_url = scrapy.Field()  # 通用字段：附件链接
    file_type = scrapy.Field()  # 通用字段：附件类型
    file_name = scrapy.Field()  # 通用字段：附件名称
    isload = scrapy.Field()  # 通用字段：是否下载成功
    file_path = scrapy.Field()  # 通用字段：附件本地存储路径
    fkey = scrapy.Field()  # 通用字段：外键
    pagenum = scrapy.Field()  # 通用字段：页码