#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time : 2019/4/2 9:57
# @Author : way
# @Site : all
# @Describe: 基础类 数据入库 HBASE

import time
import logging
import happybase
from SP.utils.make_key import rowkey, bizdate

logger = logging.getLogger(__name__)


class HbasePipeline(object):

    @classmethod
    def from_crawler(cls, crawler):
        settings = crawler.settings
        name = crawler.spider.name
        return cls(name, **settings)

    def __init__(self, name, **kwargs):
        self.table_cols_map = {}  # 表字段顺序 {table：(cols, col_default)}
        self.bizdate = bizdate  # 业务日期为启动爬虫的日期
        self.buckets_map = {}  # 桶 {table：items}
        self.name = name
        self.bucketsize = kwargs.get('BUCKETSIZE')
        self.hbase_host = kwargs.get('HBASE_HOST')
        self.hbase_port = kwargs.get('HBASE_PORT')

    def get_connect(self):
        """
        :return: 连接hbase, 返回hbase连接对象
        """
        try:
            connection = happybase.Connection(host=self.hbase_host, port=self.hbase_port, timeout=120000)  # 设置2分钟超时
            return connection
        except Exception as e:
            logger.error(f"hbase连接失败：{e}")

    def process_item(self, item, spider):
        """
        :param item:
        :param spider:
        :return: 数据分表入库
        """
        if item.tablename in self.buckets_map:
            self.buckets_map[item.tablename].append(item)
        else:
            cols, col_default = [], {}
            for field, value in item.fields.items():
                cols.append(field)
                col_default[field] = item.fields[field].get('default', '')
            cols.sort(key=lambda x: item.fields[x].get('idx', 1))
            self.table_cols_map.setdefault(item.tablename, (cols, col_default))  # 定义表结构、字段顺序、默认值
            self.buckets_map.setdefault(item.tablename, [item])
            self.checktable(item.tablename)  # 建表
        self.buckets2db()  # 将满足条件的桶 入库
        return item

    def close_spider(self, spider):
        """
        :param spider:
        :return:  爬虫结束时，将桶里面剩下的数据 入库
        """
        self.buckets2db(1)

    def checktable(self, tbname):
        """
        :return: 检查所有的目标表是否存在 hbase，不存在则创建
        """
        connection = self.get_connect()
        tables = connection.tables()
        if tbname.encode('utf-8') not in tables:
            connection.create_table(tbname, {'cf': dict()})
            logger.info(f"表创建成功 <= 表名:{tbname}")
        else:
            logger.info(f"表已存在 <= 表名:{tbname}")
        connection.close()

    def buckets2db(self, bucketsize=None):
        """
        :param bucketsize:  桶大小
        :return: 遍历每个桶，将满足条件的桶，入库并清空桶
        """
        if bucketsize is None:
            bucketsize = self.bucketsize
        for tablename, items in self.buckets_map.items():  # 遍历每个桶，将满足条件的桶，入库并清空桶
            if len(items) >= bucketsize:
                cols, col_default = self.table_cols_map.get(tablename)
                new_items = []
                for item in items:
                    keyid = rowkey()
                    values = {}
                    for field in cols:
                        value = item.get(field, col_default.get(field))
                        values['cf:' + field] = str(value)
                    values['cf:bizdate'] = self.bizdate  # 增加非业务字段
                    values['cf:ctime'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                    values['cf:spider'] = self.name
                    new_items.append((keyid, values))

                connection = self.get_connect()
                table = connection.table(tablename)
                try:
                    bat = table.batch()
                    for keyid, values in new_items:
                        bat.put(keyid, values)  # 将清洗后的桶数据 添加到批次
                    bat.send()  # 批次入库
                    logger.info(f"入库成功 <= 表名:{tablename} 记录数:{len(items)}")
                except Exception as e:
                    logger.error(f"入库失败 <= 表名:{tablename} 错误原因:{e}")
                    logger.warning(f"重新入库 <= 表名:{tablename} 当前批次入库异常, 自动切换成逐行入库...")
                    for keyid, values in new_items:
                        try:
                            table.put(keyid, values)
                            logger.info(f"入库成功 <= 表名:{tablename} 记录数:1")
                        except Exception as e:
                            logger.error(f"丢弃 <= 表名:{tablename} 丢弃原因:{e}")
                finally:
                    items.clear()  # 清空桶
                    connection.close()
