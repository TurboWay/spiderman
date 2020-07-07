#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time : 2020/5/15 13:47
# @Author : way
# @Site : all
# @Describe: 遍历item和spider，记录爬虫元数据表

import time
import sys
import os
import re
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.types import VARCHAR, INT
from SP.utils.tool import coalesce
from SP.settings import META_ENGION

ENGINE = create_engine(META_ENGION)
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
    meta = {}
    with open(items_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        table_name = ''
        for line in lines:
            line = line.strip()
            if len(line) > 0 and not line.startswith('#'):
                name = coalesce(re.findall('class (.*)_Item', line)).strip()
                if name:
                    table_name = name
                    table_comment = line.split('#')[-1].strip() if '#' in line else ''
                    meta[table_name] = [table_comment]
                elif table_name and 'scrapy.Field' in line:
                    col_name = line.split('=')[0].strip()
                    col_comment = re.findall("'comment': '(.*?)'", line)[0] if re.findall("'comment': '(.*?)'",
                                                                                          line) else ''
                    col_px = re.findall("'idx': (\d+)", line)[0] if re.findall("'idx': (\d+)", line) else 1
                    item = (col_name, col_comment, col_px)
                    meta[table_name].append(item)
    # 数据处理
    values = []
    for table_name, cols in meta.items():
        table_comment = cols.pop(0)
        cols.sort(key=lambda x: int(x[-1]))
        default_cols = [
            ('bizdate', '采集日期'),
            ('ctime', '采集时间'),
            ('spider', '爬虫名称')
        ]
        file_cols = [
            ('file_url', '附件链接'),
            ('file_type', '附件类型'),
            ('px', '文件序号'),
            ('file_name', '附件名称'),
            ('isload', '是否下载成功'),
            ('file_path', '附件本地存储路径'),
            ('fkey', '外键'),
            ('pagenum', '页码'),
        ]
        # 补充非业务字段
        if table_name.endswith('_file'):
            cols = [('keyid', '唯一标识'), ] + file_cols + cols + default_cols
        else:
            cols = [('keyid', '唯一标识'), ] + cols + default_cols
        # 遍历
        for col_px, col_item in enumerate(cols, 1):
            value = {
                'spider': spidername,
                'spider_comment': describe,
                'tb': table_name,
                'tb_comment': table_comment,
                'col_px': col_px,
                'col': col_item[0],
                'col_comment': col_item[1],
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
