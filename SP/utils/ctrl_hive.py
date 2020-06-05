#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time : 2020/5/27 17:23
# @Author : way
# @Site : 
# @Describe: 操作 hive , windows 下可能会有环境问题，参考 https://www.cnblogs.com/TurboWay/p/12975034.html

from impala.dbapi import connect
from SP.settings import HIVE_HOST, HIVE_PORT, HIVE_DBNAME

class CtrlHive:

    def __init__(self, host, port, database):
        self.connection = connect(host=host, port=port, database=database, auth_mechanism='PLAIN')

    def __del__(self):
        self.connection.close()

    def execute(self, sql):
        with self.connection.cursor() as cursor:
            cursor.execute(sql)
            try:
                rows = cursor.fetchall()
                return rows
            except:
                pass


if __name__ == "__main__":
    hv = CtrlHive(HIVE_HOST, HIVE_PORT, HIVE_DBNAME)
    sql = "show databases"
    rows = hv.execute(sql)
    print(rows)
