#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time : 2019/6/4 15:57
# @Author : way
# @Site : all
# @Describe: 基础类 保存为数据文件

import os
import time
import logging
from SP.utils.make_key import rowkey, bizdate

logger = logging.getLogger(__name__)


class DataFilePipeline(object):

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
        self.dir = kwargs.get('FILES_STORE')  # 文件夹路径
        self.type = kwargs.get('DATAFILE_TYPE', 'csv')  # 文件类型，默认 csv
        self.delimiter = kwargs.get('DATAFILE_DELIMITER', ',')  # 列分隔符, 默认','
        self.encoding = kwargs.get('DATAFILE_ENCODING', 'utf-8-sig')  # 文件编码，默认 utf-8-sig
        self.writeheader = kwargs.get('DATAFILE_HEADER', True)  # 是否写入表头列名, 默认 True

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
        self.buckets2db()  # 将满足条件的桶 入库
        return item

    def close_spider(self, spider):
        """
        :param spider:
        :return:  爬虫结束时，将桶里面剩下的数据 入库
        """
        self.buckets2db(1)

    def buckets2db(self, bucketsize=None):
        """
        :param bucketsize:  桶大小
        :return: 遍历每个桶，将满足条件的桶，入库并清空桶
        """
        if bucketsize is None:
            bucketsize = self.bucketsize
        for tablename, items in self.buckets_map.items():  # 遍历每个桶，将满足条件的桶，入库并清空桶
            if len(items) >= bucketsize:
                header = ''
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
                    if not header:
                        header = self.delimiter.join(new_item.keys())
                    value = self.delimiter.join(new_item.values())
                    # value = self.delimiter.join([new_item[key] for key in header.split(self.delimiter)])
                    new_items.append(value)

                fielder = f"{self.dir}/{self.name}"
                os.makedirs(fielder, exist_ok=True)

                filename = f"{fielder}/{tablename}.{self.type}"
                if self.writeheader:
                    if not os.path.exists(filename) or os.path.getsize(filename) == 0:
                        with open(filename, 'w', encoding=self.encoding) as f:
                            f.writelines(header + '\n')

                try:
                    with open(filename, 'a', encoding=self.encoding) as f:
                        f.write('\n'.join(new_items) + '\n')
                    logger.info(f"保存成功 <= 文件名:{filename} 记录数:{len(items)}")
                except Exception as e:
                    logger.error(f"保存失败 <= 文件名:{filename} 错误原因:{e}")
                    logger.warning(f"重新保存 <= 文件名:{tablename} 当前批次保存异常, 自动切换成逐行保存...")
                    for new_item in new_items:
                        try:
                            with open(filename, 'a', encoding=self.encoding) as f:
                                f.write(new_item + '\n')
                            logger.info(f"保存成功 <= 文件名:{tablename} 记录数:1")
                        except Exception as e:
                            logger.error(f"丢弃 <= 表名:{tablename} 丢弃原因:{e}")
                finally:
                    items.clear()  # 清空桶