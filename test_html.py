#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time : 2019/3/8 9:28
# @Author : way
# @Site :
# @Describe: html请求测试 工具

import requests
import re
from bs4 import BeautifulSoup
import time
import json


def str2dict(st):
    """
    :param st: 字符串转字典
    :return:
    """
    if isinstance(st, dict):
        return st
    dt = [item.split(':', 1) for item in st.strip().replace(': ', ':').split('\n')]
    print(dict(dt))
    return dict(dt)


def test(url, Form_Data, header):
    """
    :param url: 请求地址
    :param Form_Data: post表单, 传空时默认为 GET请求
    :param use_proxy: 使用代理ip
    :return:
    """
    print(url)
    headers = str2dict(header)
    proxies = None
    if isinstance(Form_Data, str):
        Form_Data = Form_Data.strip()
    if Form_Data:
        form = str2dict(Form_Data)
        res = requests.post(url=url, data=form, proxies=proxies, headers=headers)
    else:
        res = requests.get(url=url, proxies=proxies, headers=headers)
    # res.encoding = 'utf-8'
    with open('test.html', 'w', encoding=res.encoding) as f:
        f.write(res.text)
    print(res.status_code)
    perse(res)


def perse(response):
    # rows = BeautifulSoup(response.text, 'lxml')
    # rows = BeautifulSoup(response.text, 'xml').find_all('record')
    # rows = json.loads(response.text)
    # rows = json.loads(response.text.encode('utf-8').decode('utf-8-sig').replace('\r\n','').replace('\n',''))
    # print(response.text)
    ...


if __name__ == "__main__":
    # 请求头
    header = """
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36

"""
    # post表单，放空默认为get请求
    Form_Data = """
"""
    # 请求地址
    url = """
"""
    # use_proxy=False 默认不使用代理ip
    response = test(url.strip(), Form_Data.strip(), header.strip())
