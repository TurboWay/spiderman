#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time : 2019/3/8 15:47
# @Author : way
# @Site : 
# @Describe: 生成日志路径

import time
import os
from SP.settings import LOGDIR

logdate = time.strftime('%Y%m%d', time.localtime())


def log(name):
    # 生成日志文件夹
    logpath = f'{LOGDIR}/{logdate}'
    os.makedirs(logpath, exist_ok=True)

    # 生成日志路径
    logfile = f'{logpath}/{name}.log'
    return logfile