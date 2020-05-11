#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time : 2019/4/2 9:57
# @Author : way
# @Site : all
# @Describe: 基础类 数据清洗入库 HBASE

import time
import logging
import happybase
from SP.settings import BUCKETSIZE, HBASE_HOST, HBASE_PORT
from SP.utils.make_key import rowkey, bizdate
from SP.utils.tool import clean


class HbasePipeline(object):

    def __init__(self, item_table_map):
        self.item_table_map = item_table_map  # {} key为 Item类型， value为tablename
        self.bizdate = bizdate  # 业务日期为启动爬虫的日期
        self.buckets_map = {}  # 桶 {table：items}
        self.checktable()  # 建表

    @staticmethod
    def get_connect():
        """
        :return: 连接hbase, 返回hbase连接对象
        """
        try:
            connection = happybase.Connection(host=HBASE_HOST, port=HBASE_PORT, timeout=120000)  # 设置2分钟超时
            return connection
        except Exception as e:
            logging.error(f"hbase连接失败：{e}")

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

    def checktable(self):
        """
        :return: 检查所有的目标表是否存在 hbase，不存在则创建
        """
        connection = self.get_connect()
        tables = connection.tables()
        for tbname in self.item_table_map.values():
            if tbname.encode('utf-8') not in tables:
                connection.create_table(tbname, {'cf': dict()})
                logging.info(f"表创建成功 <= 表名:{tbname}")
            else:
                logging.info(f"表已存在 <= 表名:{tbname}")
        connection.close()

    def buckets2db(self, bucketsize=100, spider_name=''):
        """
        :param bucketsize:  桶大小
        :param spider_name:  爬虫名字
        :return: 遍历每个桶，将满足条件的桶，入库并清空桶
        """
        for tablename, items in self.buckets_map.items():  # 遍历每个桶，将满足条件的桶，入库并清空桶
            if len(items) >= bucketsize:
                connection = self.get_connect()
                table = connection.table(tablename)
                bat = table.batch()
                for item in items:
                    keyid = rowkey()
                    values = {}
                    for key, value in item.items():  # 清洗桶数据
                        try:
                            value = clean(value)
                        except Exception as e:
                            value = 'ERROR'
                            logging.error(f"hbase入库预处理异常: 表名:{tablename} KeyID:{keyid} 错误原因:{e}")
                        finally:
                            values['cf:' + key] = value
                    values['cf:bizdate'] = self.bizdate  # 增加非业务字段
                    values['cf:ctime'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                    values['cf:spider'] = spider_name
                    bat.put(keyid, values)  # 将清洗后的桶数据 添加到批次
                try:
                    bat.send()  # 批次入库
                    logging.info(f"入库成功 <= 表名:{tablename} 记录数:{len(items)}")
                    items.clear()  # 清空桶
                except Exception as e:
                    logging.error(f"入库失败 <= 表名:{tablename} 错误原因:{e}")
                finally:
                    connection.close()
