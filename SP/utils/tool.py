#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time : 2019/4/11 16:39
# @Author : way
# @Site :
# @Describe: 工具函数

import re
import time
import base64
from hashlib import md5
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from SP.settings import ENGINE_CONFIG


def clean(value):
    """
    数据入库前,清洗通用方法
    :param value: 采集值
    :return: 清洗后的值
    """
    if value is None:
        return ''
    move = dict.fromkeys((ord(c) for c in "\001\xa0\n\t\x0d\x0a"))  # 字段清洗规则
    clean_value = str(value).translate(move).strip()
    return clean_value


def coalesce(lts):
    """
    返回第一个非空值，可以配合正则使用
    :param lts: str 或者 list类型
    :return: 第一个非空值，如果是list，则返回第一个元素
    """
    lts = [lts] if not isinstance(lts, list) else lts  # 兼容其他类型传参
    for lt in lts:
        if lt:
            if isinstance(lt, list):
                return lt[0]
            else:
                return lt
    return ''


def encode_md5(st):
    """
    :param st: str
    :return: md5加密后的密文
    """
    new_md5 = md5()
    new_md5.update(st.encode(encoding='utf-8'))
    return new_md5.hexdigest()


def encode_base64(st):
    """
    base64加密
    :param st: str
    :return: base64加密后的密文
    """
    encode = base64.b64encode(st.encode('utf-8'))
    return str(encode, 'utf-8')


def decode_base64(st):
    """
    base64解密
    :param st: str
    :return: base64解密后的明文
    """
    decode = base64.b64decode(st.encode('utf-8'))
    return str(decode, 'utf-8')


def deal_time_stamp(time_stamp, unit='ms', format='%Y-%m-%d'):
    """
    时间戳转换成日期格式
    :param time_stamp: 时间戳
    :param unit: 时间单位，默认为毫秒(ms)，其他为秒(s)
    :return: 转换好的时间格式，默认年-月-日
    """
    timeArray = time.localtime(int(int(time_stamp) / 1000)) if unit == 'ms' else time.localtime(int(time_stamp))
    otherStyleTime = time.strftime(format, timeArray)
    return otherStyleTime


def get_file_type(*args):
    """
    返回文件类型
    :return: 文件类型
    """
    file_types = [
        'pdf', 'ppt', 'xls', 'xlsx', 'doc', 'docx', 'txt', 'wps',  # office文件类型
        'bmp', 'gif', 'jpg', 'jpeg', 'png', 'tif', 'swf',  # img 类型
        'rar', 'zip', 'arj', 'gz', 'tar', 'tar.gz', '7z',  # 压缩包类型
        'rmvb', 'mp4', 'rm', 'mpg', 'mpeg', 'avi', 'mov', 'wmv',  # 视频类型
        'mid', 'mp3', 'wma', 'wav',  # 音频类型
    ]
    for lt in args:
        # http 类型处理
        file_type = lt.split('.')[-1]
        if '&' in file_type:
            file_type = file_type.split('&')[0]
        if '?' in file_type:
            file_type = file_type.split('?')[0]
        if file_type.strip().lower() in file_types:
            return file_type
        # data url类型处理
        file_type = coalesce(re.findall("data:image/(.*);", lt))
        if file_type.strip().lower() in file_types:
            return file_type
    return ''


def url_check(url, dirty_words=None):
    """
    url 的可用性检查，可用返回True 不可用返回False【根据脏字过滤url】
    :param url: 根据脏字 检查url是否可用
    :return: 可用返回 True 不可用 False
    """
    keywords = [
        'baidu.com', 'javascript', 'mailto:', 'sougou.com',
        '@qq.com', '@gmail.com', '@163.com', '@yahoo.com', '@msn.com', '@hotmail.com', '@aol.com', '@ask.com',
        '@live.com', '@0355.net', '@163.net', '@263.net', '@3721.net', '@yeah'
    ]
    if dirty_words:  # 自定义脏字
        dirty_words = [dirty_words] if not isinstance(dirty_words, list) else dirty_words  # 兼容其他类型传参
        keywords += dirty_words

    for keyword in keywords:
        if keyword in url:
            return False
    return True


def rdbm_execute(sql):
    """
    执行sql
    :param sql:
    :return:
    """
    engine = create_engine(ENGINE_CONFIG)
    Session = sessionmaker(bind=engine)
    session = Session()
    rows = session.execute(sql).fetchall()
    session.close()
    return rows
