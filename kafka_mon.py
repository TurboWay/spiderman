#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time : 2020/5/18 14:50
# @Author : way
# @Site : 
# @Describe:  kafka 实时监控

"""
主题名 = 爬虫名
key名 = 爬虫表名
"""
import json
import re
from kafka import KafkaConsumer
from SP.settings import KAFKA_SERVERS

consumer = KafkaConsumer(bootstrap_servers=KAFKA_SERVERS,
                         # auto_offset_reset='earliest', # 重置偏移量 earliest移到最早的可用消息，latest最新的消息，默认为latest
                         key_deserializer=lambda m: m.decode('utf-8'),
                         value_deserializer=lambda m: json.loads(m.decode('utf-8')))
consumer.subscribe(topics=['zhifang', ])  # 订阅主题
for msg in consumer:
    # print(msg)
    # print(msg.key, msg.value)
    if msg.key == 'zhifang_list':   # 实时采集，监控 单价小于 8000元/平米的 房源
        price = msg.value.get('price')
        price = re.findall('单价(\d+)元', price)
        if price and int(price[0]) < 8000:
            print(msg.value.get('price'), msg.value.get('title'), msg.value.get('detail_full_url'))
