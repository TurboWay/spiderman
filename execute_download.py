#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time : 2021/3/16 21:12
# @Author : way
# @Site : 
# @Describe:

import sys
import getopt
import random
from concurrent.futures import ThreadPoolExecutor
from download import logger, BIZDATE, DownLoad
from SP.utils.ctrl_ssh import SSH
from SP.settings import CLUSTER_ENABLE, SLAVES, SLAVES_BALANCE, SLAVES_ENV, SLAVES_WORKSPACE

##################################################### 【传参配置】######################################################
helpmsg = f"""
Usage:
    python easy_download.py [options]

Options:
    -s, --spider        【必要传参】爬虫名称
    -b, --bizdate       业务日期，作为过滤条件，默认 bizdate={BIZDATE}
    -j, --jobtype       启动类型, 默认 jobtype = runjob
                        可选的操作：job      只生成任务
                                    run      只启动下载
                                    runjob   生成任务并启动下载
    -n, --num           分布式下载时，启动的机器数量，默认单机下载 num=1
    -m, --max_workers   文件下载并发数, 默认 max_workers=10
    -d, --delay         下载延迟，默认 delay=0    
    -r, --retry         重试次数，默认 retry=3
    -o, --overwrite     重新下载开关，默认 overwrite=false
                        可选操作： 
                        true    不管文件是否存在，重新下载
                        false   文件已存在，则跳过
    -h, --help          查看帮助
"""
# 打印帮助信息
if sys.argv.__len__() > 1 and sys.argv[1] in ('-h', '-help', '--help'):
    print(helpmsg)
    sys.exit(1)

opts, args = getopt.getopt(sys.argv[1:],
                           "s:b:j:n:m:d:r:o:",
                           ["spider=", "bizdate=", "jobtype", "num", "max_workers=", "delay=", "retry=", "overwrite="])
spider = ''  # 爬虫名字
bizdate = BIZDATE  # 业务日期
jobtype = 'runjob'  # 启动类型
num = 1  # 启动的机器数量
max_workers = 10  # 文件下载并发数
delay = 0  # 下载延迟
retry = 3  # 重试次数
overwrite = False  # 重新下载开关

for op, value in opts:
    if op in ("-s", "--spider"):
        spider = value
    elif op in ("-b", "--bizdate"):
        bizdate = value
    elif op in ("-j", "--jobtype"):
        jobtype = value
    elif op in ("-n", "--num"):
        num = int(value)
    elif op in ("-m", "--max_workers"):
        max_workers = int(value)
    elif op in ("-d", "--delay"):
        delay = int(value)
    elif op in ("-r", "--retry"):
        retry = int(value)
    elif op in ("-o", "--overwrite"):
        if value in ('true', 'True'):
            overwrite = True

if not spider:
    print("options error ! \n"
          "you can use the following command to get some help: \n"
          "python download.py --help")
    sys.exit(1)

order = 'python ' + ' '.join(sys.argv)
logger.info(f"运行命令：{order}")
download = DownLoad(spider=spider, bizdate=bizdate, max_workers=max_workers, delay=delay, retry=retry,
                    overwrite=overwrite)

if jobtype in ('job', 'runjob'):
    download.delete()
    download.make_job()
    logger.info(f"生成成功，{download.redis_key} 待下载的附件数为 {download.get_job_size()}")

if jobtype in ('run', 'runjob') and num == 1:
    if download.get_job_size() > 0:
        download.run()
    else:
        logger.info(f"{download.redis_key} 待下载的附件数为 0")

if jobtype in ('run', 'runjob') and num > 1:
    def ssh_run(*args):
        slave = random.sample(SLAVES, 1)[0] if not SLAVES_BALANCE else SLAVES_BALANCE
        if SLAVES_ENV:
            cmd = f'source {SLAVES_ENV}/bin/activate; cd {SLAVES_WORKSPACE}; {order} -j run -n 1;'
        else:
            cmd = f"cd {SLAVES_WORKSPACE}; {order} -j run -n 1;"
        ssh = SSH(slave)
        hostname = ssh.hostname
        logger.info(f"slave:{hostname} 正在下载附件...")
        status, msg_out, msg_error = ssh.execute(cmd)
        if status != 0:
            logger.error(f"slave:{hostname} 附件下载失败：{msg_out + msg_error}")
        else:
            logger.info(f"slave:{hostname} 附件下载完成")


    if not CLUSTER_ENABLE:
        logger.error(f"请在 setting 中启用集群模式 CLUSTER_ENABLE ！")
        sys.exit(1)
    if not (SLAVES or SLAVES_BALANCE):
        logger.error(f"请在 setting 中配置 SLAVES 机器！")
        sys.exit(1)
    size = download.get_job_size()
    logger.info(f"{download.redis_key} 初始任务数: {size} 启动爬虫数量: {num}")
    if size > 0:
        pool = ThreadPoolExecutor(max_workers=num)
        for _ in pool.map(ssh_run, range(num)):
            ...  # 等待所有线程完成
