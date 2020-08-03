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
    file_url = scrapy.Field({'idx': 1, 'comment': '附件链接'})
    file_type = scrapy.Field({'idx': 2, 'comment': '附件类型'})
    px = scrapy.Field({'idx': 3, 'comment': '文件序号'})
    file_name = scrapy.Field({'idx': 4, 'comment': '附件名称'})
    status = scrapy.Field({'idx': 5, 'comment': '下载状态', 'default': '未下载'})
    file_path = scrapy.Field({'idx': 6, 'comment': '文件存储路径'})
    fkey = scrapy.Field({'idx': 7, 'comment': '外键'})
    pagenum = scrapy.Field({'idx': 8, 'comment': '页码'})
