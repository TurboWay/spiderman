#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time : 2020/5/14 15:45
# @Author : way
# @Site : 
# @Describe: 操作ssh

import paramiko


# ssh 执行命令
class SSH:

    def __init__(self, slave):
        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.ssh.connect(
            hostname=slave['host'],
            port=slave['port'],
            username=slave['user'],
            password=slave['pwd']
        )

    @property
    def hostname(self):
        status, msg_out, msg_error = self.execute('hostname')
        return msg_out.strip('\n')

    def execute(self, cmd):
        stdin, stdout, stderr = self.ssh.exec_command(cmd)
        channel = stdout.channel
        status = channel.recv_exit_status()
        msg_out = stdout.read().decode('utf-8')
        msg_error = stderr.read().decode('utf-8')
        return status, msg_out, msg_error
