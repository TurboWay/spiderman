#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time : 2019/6/4 17:07
# @Author : way
# @Site : all
# @Describe: 基础类 保存到 hdfs

import time
import logging
from hdfs import Client
from SP.utils.make_key import rowkey, bizdate
from SP.utils.ctrl_hive import CtrlHive

logger = logging.getLogger(__name__)


class HdfsPipeline(object):

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
        self.client = Client(kwargs.get('HDFS_URLS'))
        self.dir = kwargs.get('HDFS_FOLDER')  # 文件夹路径
        self.delimiter = kwargs.get('HDFS_DELIMITER')  # 列分隔符,默认 hive默认分隔符
        self.encoding = kwargs.get('HDFS_ENCODING')  # 文件编码，默认 'utf-8'
        self.hive_host = kwargs.get('HIVE_HOST')
        self.hive_port = kwargs.get('HIVE_PORT')
        self.hive_dbname = kwargs.get('HIVE_DBNAME')  # 数据库名称
        self.hive_auto_create = kwargs.get('HIVE_AUTO_CREATE', False)  # hive 是否自动建表，默认 False
        self.client.makedirs(self.dir)

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
            if self.hive_auto_create:
                self.checktable(item.tablename, cols)  # 建表
        self.buckets2db()  # 将满足条件的桶 入库
        return item

    def close_spider(self, spider):
        """
        :param spider:
        :return:  爬虫结束时，将桶里面剩下的数据 入库
        """
        self.buckets2db(1)

    def checktable(self, tbname, cols):
        """
        :return: 创建 hive 表
        """
        hive = CtrlHive(self.hive_host, self.hive_port, self.hive_dbname)
        cols = ['keyid'] + cols + ['bizdate', 'ctime', 'spider']
        create_sql = f"create table if not exists {tbname}({' string,'.join(cols)} string)"
        hive.execute(create_sql)
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
                new_items = []
                cols, col_default = self.table_cols_map.get(tablename)
                for item in items:
                    keyid = rowkey()
                    new_item = {'keyid': keyid}
                    for field in cols:
                        value = item.get(field, col_default.get(field))
                        new_item[field] = str(value).replace(self.delimiter, '').replace('\n', '')
                    new_item['bizdate'] = self.bizdate  # 增加非业务字段
                    new_item['ctime'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                    new_item['spider'] = self.name
                    value = self.delimiter.join(new_item.values())
                    new_items.append(value)

                # 每张表是都是一个文件夹
                folder = f"{self.dir}/{tablename}"
                self.client.makedirs(folder)

                filename = f"{folder}/data.txt"
                info = self.client.status(filename, strict=False)
                if not info:
                    self.client.write(filename, data='', overwrite=True, encoding=self.encoding)

                try:
                    content = '\n'.join(new_items) + '\n'
                    self.client.write(filename, data=content, overwrite=False, append=True, encoding=self.encoding)
                    logger.info(f"保存成功 <= 文件名:{filename} 记录数:{len(items)}")
                except Exception as e:
                    logger.error(f"保存失败 <= 文件名:{filename} 错误原因:{e}")
                    logger.warning(f"重新保存 <= 文件名:{tablename} 当前批次保存异常, 自动切换成逐行保存...")
                    for new_item in new_items:
                        try:
                            content = new_item + '\n'
                            self.client.write(filename, data=content, overwrite=False, append=True,
                                              encoding=self.encoding)
                            logger.info(f"保存成功 <= 文件名:{tablename} 记录数:1")
                        except Exception as e:
                            logger.error(f"丢弃 <= 表名:{tablename} 丢弃原因:{e}")
                finally:
                    items.clear()  # 清空桶
