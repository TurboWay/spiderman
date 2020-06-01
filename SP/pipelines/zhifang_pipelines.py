#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time : 2020-05-09 15:31
# @Author : way

from SP.pipelines.pipelines_elasticsearch import ElasticSearchPipeline as SPElasticSearchPipeline
from SP.pipelines.pipelines_kafka import KafkaPipeline as SPKafkaPipeline
from SP.pipelines.pipelines_mongodb import MongodbPipeline as SPMongodbPipeline
from SP.pipelines.pipelines_hbase import HbasePipeline as SPHbasePipeline
from SP.pipelines.pipelines_rdbm import RdbmPipeline as SPRdbmPipeline
from SP.items.zhifang_items import *
from sqlalchemy.types import VARCHAR

# habse爬虫表名定义
list_table = 'zhifang_list'
detail_table = 'zhifang_detail'
file_table = 'zhifang_file'

# Item 和 habse爬虫表 映射
item_table_map = {
    zhifang_list_Item: list_table,
    zhifang_detail_Item: detail_table,
    zhifang_file_Item: file_table
}

# 关系型数据库，可以自定义某些字段的类型长度，默认 VARCHAR(length=255)
col_type = {
    # 'title': VARCHAR(length=255)
}


class RdbmPipeline(SPRdbmPipeline):

    def __init__(self):
        super().__init__(item_table_map=item_table_map, col_type=col_type)


class HbasePipeline(SPHbasePipeline):

    def __init__(self):
        super().__init__(item_table_map=item_table_map)


class MongodbPipeline(SPMongodbPipeline):

    def __init__(self):
        super().__init__(item_table_map=item_table_map)


class KafkaPipeline(SPKafkaPipeline):

    def __init__(self):
        super().__init__(item_table_map=item_table_map)


class ElasticSearchPipeline(SPElasticSearchPipeline):

    def __init__(self):
        super().__init__(item_table_map=item_table_map)
