#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time : 2020/5/18 10:16
# @Author : way
# @Site : 
# @Describe: 数据实时写到 kafka

import json
import time
import logging
from kafka import KafkaProducer
from random import choice

logger = logging.getLogger(__name__)


class KafkaPipeline(object):

    @classmethod
    def from_crawler(cls, crawler):
        settings = crawler.settings
        name = crawler.spider.name
        return cls(name, **settings)

    def __init__(self, name, **kwargs):
        self.kafkaproducer = KafkaProducer(bootstrap_servers=kwargs.get('KAFKA_SERVERS'),
                                           key_serializer=lambda m: m.encode('utf-8'),
                                           value_serializer=lambda m: json.dumps(m).encode('utf-8'))
        self.partitions = list(self.kafkaproducer.partitions_for(name)) # 获取所有分区

    def process_item(self, item, spider):
        """
        :param item:
        :param spider:
        :return: 数据分表入库
        """
        new_item = {key: value for key, value in item.items()}
        new_item['ctime'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        try:
            self.kafkaproducer.send(topic=spider.name, partition=choice(self.partitions), key=item.tablename, value=new_item).get(timeout=10)
            logger.info(f"入库成功 <= 主题:{spider.name} key名:{item.tablename}")
        except Exception as e:
            logger.error(f"入库失败 <= 主题:{spider.name} key名:{item.tablename} 错误原因:{e}")
        return item
