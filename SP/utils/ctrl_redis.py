#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time : 2021/3/15 20:47
# @Author : way
# @Site : 
# @Describe: 操作 redis

import redis
import json
import logging
from SP.settings import REDIS_HOST, REDIS_PORT


# 操作redis基础类
class RedisCtrl:

    def __init__(self):
        self.pool = redis.ConnectionPool(host=REDIS_HOST, port=REDIS_PORT)
        self.r = redis.Redis(connection_pool=self.pool)

    def reqs_push(self, redis_key, reqs):
        """
        :param redis_key:
        :param reqs:
        :return: 将请求推到指定的redis_key中
        """
        try:
            pipe = self.r.pipeline(transaction=True)
            for req in reqs:
                self.r.rpush(redis_key, json.dumps(req.__dict__, ensure_ascii=False))
            pipe.execute()
        except Exception as e:
            logging.error(f"redis写入失败：{e}")

    def keys_del(self, keys):
        """
        :param keys: list
        :return: 删除redis中的指定key
        """
        try:
            pipe = self.r.pipeline(transaction=True)
            for key in keys:
                self.r.delete(key)
            pipe.execute()
        except Exception as e:
            logging.error(f"redis删除失败：{e}")

    def key_len(self, key):
        """
        :param key:
        :return: 获取redis_key的数量长度
        """
        try:
            size = self.r.llen(key)
            return size
        except Exception as e:
            logging.error(f"redis读取失败：{e}")

    def copy(self, source_key, target_key):
        """
        :param source_key:
        :param target_key:
        :return: 备份redis数据，从source_key备份到target_key
        """
        try:
            pipe = self.r.pipeline(transaction=True)
            vals = self.r.lrange(source_key, 0, -1)
            self.r.delete(target_key)
            for val in vals:
                self.r.rpush(target_key, val)
            pipe.execute()
        except Exception as e:
            logging.error(f"redis复制失败：{e}")

    def add_string(self, key, value):
        """
        :param key:
        :param value:
        :return: 写入 redis string
        """
        try:
            self.r.set(key, value)
        except Exception as e:
            logging.error(f"redis写入失败：{e}")

    def get_string(self, key):
        """
        :param key:
        :return: 读取 string
        """
        try:
            return self.r.get(key).decode()
        except Exception as e:
            logging.error(f"redis写入失败：{e}")

    def add_set(self, key, *args):
        """
        :param key:
        :param value:
        :return: 写入 redis set
        """
        try:
            self.r.sadd(key, *args)
        except Exception as e:
            logging.error(f"redis写入失败：{e}")

    def remove_set(self, key, value):
        """
        :param key: redis_key.key
        :return: 删除redis_key中的指定记录key
        """
        try:
            self.r.srem(key, value)
        except Exception as e:
            logging.error(f"redis删除失败：{e}")

    def get_set(self, key):
        """
        :return: 从redis_key中取出所有值
        """
        try:
            return [i.decode() for i in self.r.smembers(key)]
        except Exception as e:
            logging.error(f"redis读取失败：{e}")