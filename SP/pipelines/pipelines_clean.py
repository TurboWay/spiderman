#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time : 2020/5/18 15:43
# @Author : way
# @Site : 
# @Describe: 通用字段清洗管道

import logging
from SP.utils.tool import clean

logger = logging.getLogger(__name__)


class CleanPipeline(object):

    def process_item(self, item, spider):
        """
        :param item:
        :param spider:
        :return: 数据分表入库
        """
        for key, value in item.items():  # 清洗桶数据
            try:
                value = clean(value)
            except Exception as e:
                logger.error(f"入库前数据清洗异常, 值:{value}, 错误原因:{e}")
            finally:
                item[key] = value
        return item
