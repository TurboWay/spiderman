#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time : 2023/2/10 17:14
# @Author : way
# @Site : 
# @Describe:

import time
import logging
from DorisClient import DorisSession
from SP.utils.base import rowkey, bizdate

logger = logging.getLogger(__name__)


class DorisPipeline(object):

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
        self.doris_cfg = kwargs.get('DORIS_CFG')

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
            self.checktable(item.tablename, cols)  # 建表
        self.buckets2db()  # 将满足条件的桶 入库
        return item

    def close_spider(self, spider):
        """
        :param spider:
        :return:  爬虫结束时，将桶里面剩下的数据 入库
        """
        self.buckets2db(1)

    def get_connect(self):
        """
        :return: 连接doris, 返回DorisSession
        """
        return DorisSession(**self.doris_cfg)

    def checktable(self, tbname, cols):
        """
        :return: 检查所有的目标表是否存在 hbase，不存在则创建
        """
        cols += ['bizdate', 'ctime', 'spider']
        cols = map(lambda x:f'`{x}`', cols)
        create_sql = f"create table if not exists {tbname}(`keyid` varchar(50), {' string,'.join(cols)} string) DISTRIBUTED BY HASH(`keyid`) BUCKETS 2;"
        # logger.info(create_sql)
        self.get_connect().execute(create_sql)
        logger.info(f"表创建成功 <= 表名:{tbname}")

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
                    values = {'keyid': rowkey()}
                    for field in cols:
                        value = item.get(field, col_default.get(field))
                        values[field] = str(value)
                    values['bizdate'] = self.bizdate  # 增加非业务字段
                    values['ctime'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                    values['spider'] = self.name
                    new_items.append(values)
                doris = self.get_connect()
                try:
                    if doris.streamload(tablename, new_items):
                        logger.info(f"入库成功 <= 表名:{tablename} 记录数:{len(items)}")
                    else:
                        raise Exception("streamload error")
                except Exception as e:
                    logger.error(f"入库失败 <= 表名:{tablename} 错误原因:{e}")
                    logger.warning(f"重新入库 <= 表名:{tablename} 当前批次入库异常, 自动切换成逐行入库...")
                    for new_item in new_items:
                        try:
                            if doris.streamload(tablename, [new_item]):
                                logger.info(f"入库成功 <= 表名:{tablename} 记录数:1")
                            else:
                                raise Exception("streamload error")
                        except Exception as e:
                            logger.error(f"丢弃 <= 表名:{tablename} 丢弃原因:{e}")
                finally:
                    items.clear()  # 清空桶
