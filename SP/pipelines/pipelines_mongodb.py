#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time : 2019/5/12 9:57
# @Author : way
# @Site : all
# @Describe: 基础类 数据清洗入库 mongodb

import time
import logging
from pymongo import MongoClient
from SP.settings import BUCKETSIZE, MONGODB_HOST, MONGODB_PORT, MONGODB_DB
from SP.utils.make_key import rowkey, bizdate
from SP.utils.tool import clean


class MongodbPipeline(object):

    def __init__(self, item_table_map):
        self.item_table_map = item_table_map  # {} key为 Item类型， value为tablename
        self.bizdate = bizdate  # 业务日期为启动爬虫的日期
        self.buckets_map = {}  # 桶 {table：items}
        self.mongodb = MongoClient(host=MONGODB_HOST, port=MONGODB_PORT)[MONGODB_DB]

    def process_item(self, item, spider):
        """
        :param item:
        :param spider:
        :return: 数据分表入库
        """
        for Item, tbname in self.item_table_map.items():  # 判断item属于哪个表，放入对应表的桶里面
            if isinstance(item, Item):
                items = self.buckets_map.get(tbname)
                if items:
                    items.append(item)
                else:
                    self.buckets_map[tbname] = [item]
        self.buckets2db(bucketsize=BUCKETSIZE, spider_name=spider.name)  # 将满足条件的桶 入库
        return item

    def close_spider(self, spider):
        """
        :param spider:
        :return:  爬虫结束时，将桶里面剩下的数据 入库
        """
        self.buckets2db(bucketsize=1, spider_name=spider.name)

    def buckets2db(self, bucketsize=100, spider_name=''):
        """
        :param bucketsize:  桶大小
        :param spider_name:  爬虫名字
        :return: 遍历每个桶，将满足条件的桶，入库并清空桶
        """
        for tablename, items in self.buckets_map.items():  # 遍历每个桶，将满足条件的桶，入库并清空桶
            if len(items) >= bucketsize:
                new_items = []
                for item in items:
                    keyid = rowkey()
                    new_item = {'_id': keyid}
                    for key, value in item.items():  # 清洗桶数据
                        try:
                            value = clean(value)
                        except Exception as e:
                            value = 'ERROR'
                            logging.error(f"rdbm入库预处理异常: 表名:{tablename} KeyID:{keyid} 错误原因:{e}")
                        finally:
                            new_item[key] = value
                    new_item['bizdate'] = self.bizdate  # 增加非业务字段
                    new_item['ctime'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                    new_item['spider'] = spider_name
                    new_items.append(new_item)
                try:
                    self.mongodb[tablename].insert_many(new_items)
                    logging.info(f"入库成功 <= 表名:{tablename} 记录数:{len(items)}")
                    items.clear()  # 清空桶
                except Exception as e:
                    logging.error(f"入库失败 <= 表名:{tablename} 错误原因:{e}")
