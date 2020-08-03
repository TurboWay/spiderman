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

logger = logging.getLogger(__name__)


class KafkaPipeline(object):

    @classmethod
    def from_crawler(cls, crawler):
        settings = crawler.settings
        return cls(**settings)

    def __init__(self, **kwargs):
        self.kafkaproducer = KafkaProducer(bootstrap_servers=kwargs.get('KAFKA_SERVERS'),
                                           key_serializer=lambda m: m.encode('utf-8'),
                                           value_serializer=lambda m: json.dumps(m).encode('utf-8'))

    def process_item(self, item, spider):
        """
        :param item:
        :param spider:
        :return: 数据分表入库
        """
        new_item = {key: value for key, value in item.items()}
        new_item['ctime'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        try:
            self.kafkaproducer.send(topic=spider.name, key=item.tablename, value=new_item).get(timeout=10)
            logger.info(f"入库成功 <= 主题:{spider.name} key名:{item.tablename}")
        except Exception as e:
            logger.error(f"入库失败 <= 主题:{spider.name} key名:{item.tablename} 错误原因:{e}")
        return item
