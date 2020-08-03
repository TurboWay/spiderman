#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time : 2020/5/15 13:47
# @Author : way
# @Site : all
# @Describe: 遍历item和spider，记录爬虫元数据表

import os
import sys

sys.path.append(os.getcwd() + '\SP')
import time
import re
import pandas as pd
import importlib
from sqlalchemy import create_engine, types
from sqlalchemy.types import VARCHAR, INT
from SP.utils.tool import coalesce
from SP.settings import META_ENGINE

ENGINE = create_engine(META_ENGINE)
META_TABLE = 'meta'
META_COL_MAP = {
    'spider': VARCHAR(length=50),
    'spider_comment': VARCHAR(length=100),
    'tb': VARCHAR(length=50),
    'tb_comment': VARCHAR(length=100),
    'col_px': INT,
    'col': VARCHAR(length=50),
    'col_comment': VARCHAR(length=100),
    'author': VARCHAR(length=20),
    'addtime': VARCHAR(length=20),
    'insertime': VARCHAR(length=20),
}


def refresh_meta(spidername):
    # 获取爬虫文件信息
    items_path = f'{os.getcwd()}\SP\items\{spidername}_items.py'
    spider_path = f'{os.getcwd()}\SP\spiders\{spidername}.py'
    if not os.path.exists(spider_path):
        raise Exception(f"{spider_path} 爬虫文件不存在!!")
    if not os.path.exists(items_path):
        raise Exception(f"{items_path} 爬虫文件不存在!!")

    # 获取爬虫信息
    describe, author, addtime = '', '', ''
    with open(spider_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()[:10]
        for line in lines:
            if not describe:
                describe = coalesce(re.findall('@Describe.*?:(.*)', line)).strip()
            if not author:
                author = coalesce(re.findall('@Author.*?:(.*)', line)).strip()
            if not addtime:
                addtime = coalesce(re.findall('@Time.*?:(.*)', line)).strip()

    # 获取表字段信息
    meta = []
    module_name = f'SP.items.{spidername}_items'
    module = importlib.import_module(module_name)
    for item in dir(module):
        if item in ('SPfileItem', 'SPItem') or item in types.__all__:
            continue
        item = getattr(module, item)
        if isinstance(item, type):
            cols = [
                ('keyid', -99, '唯一标识'),
                ('bizdate', 1001, '业务日期'),
                ('ctime', 1002, '入库时间'),
                ('spider', 1003, '爬虫名称')
            ]
            for col in item.fields:
                idx = item.fields[col].get('idx', 0)
                comment = item.fields[col].get('comment', '')
                cols.append((col, idx, comment))
            cols.sort(key=lambda x: x[1])
            meta.append((item.tablename, item.tabledesc, cols))

    # 数据处理
    values = []
    for info in meta:
        table_name, table_comment, cols = info
        for col_px, col_item in enumerate(cols, 1):
            value = {
                'spider': spidername,
                'spider_comment': describe,
                'tb': table_name,
                'tb_comment': table_comment,
                'col_px': col_px,
                'col': col_item[0],
                'col_comment': col_item[-1],
                'author': author,
                'addtime': addtime,
                'insertime': time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            }
            values.append(value)
    # 删除旧的元数据
    if pd.io.sql.has_table(META_TABLE, con=ENGINE, schema=None):
        sql = f"delete from {META_TABLE} where spider = '{spidername}';"
        pd.read_sql(sql, ENGINE, chunksize=1)
    # 更新元数据
    df = pd.DataFrame(values, columns=[key for key in META_COL_MAP.keys()])
    df.to_sql(META_TABLE, con=ENGINE, index=False, if_exists='append', dtype=META_COL_MAP)
    print(f"*** {spidername} meta has refresh successfully!")


def main(spider):
    if spider == 'all':
        spider_dir = f"{os.getcwd()}\SP\spiders"
        for path in os.listdir(spider_dir):
            if path.endswith('.py') and path not in ('SPRedisSpider.py', '__init__.py'):
                spider = path.split('.')[0]
                refresh_meta(spider)
    else:
        refresh_meta(spider)


if __name__ == "__main__":
    spider = 'all'  # 爬虫名字

    if sys.argv.__len__() >= 2:
        spider = sys.argv[1]
    main(spider)
