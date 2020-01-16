#!/usr/bin/env python
# coding=utf-8
"""
@Desc: A utility to monitor established tcp connection if it
exceeds the given value then notifies in the Enterprise We-chat group
@author: sharp G.
@created: 20200101
"""

import json
import time
import requests
import subprocess
from datetime import datetime
# from apscheduler.schedulers.blocking import BlockingScheduler
from config import QY_WEIXIN_API, SCHEDULER_INTERVAL, MAX_ESTABLISHED_TCP_CONNECTION


class Shell(object):
    @staticmethod
    def check_output(cmd):
        """
        Implementation subprocess.check_output() for Python 2.6
        reference: https://docs.python.org/2/library/subprocess.html#subprocess.Popen
        :param cmd:
        :return: the output of shell command
        """
        process_list = []
        cmd_list = cmd.strip().split("|")
        for i, sub_cmd in enumerate(cmd_list):
            stdin = None
            if i > 0:
                stdin = process_list[i - 1].stdout
            process_list.append(subprocess.Popen(sub_cmd, stdin=stdin, stdout=subprocess.PIPE, shell=True))
        if len(process_list) == 0:
            return ''
        output = process_list[i].communicate()[0]
        return output


class Http(object):
    HEADER = {'Content-Type': 'application/json'}

    def http_request(self, msg_content):
        msg = json.dumps({"msgtype": "text", "text": {"content": msg_content}})
        requests.post(QY_WEIXIN_API, headers=self.HEADER, data=msg)


class Job(object):
    def __init__(self):
        self.shell = Shell()

    def tcp_detecting(self):
        http = Http()
        curr_time = str(datetime.now())
        cmd_ip = "ifconfig eth0 |grep 'inet addr' " \
                 "|awk -F ' ' '{print $2}' |awk -F ':' '{print $2}'"
        cmd_tcp = "netstat -n | awk '/^tcp/ {++y[$NF]} END {for(w in y) print w, y[w]}'" \
                  " |grep ESTABLISHED | awk -F ' ' '{print $2}'"
        curr_ip = self.shell.check_output(cmd_ip)
        tcp_established = self.shell.check_output(cmd_tcp)
        if int(tcp_established) > MAX_ESTABLISHED_TCP_CONNECTION:
            http.http_request(curr_ip + ': ' + '服务器当前TCP established连接数为' + str(tcp_established)
                              + ', 超过最大值' + str(MAX_ESTABLISHED_TCP_CONNECTION) + ' ' + curr_time)


if __name__ == '__main__':
    # scheduler = BlockingScheduler()
    # scheduler.add_job(job.tcp_detecting, 'interval', seconds=SCHEDULER_INTERVAL)
    # scheduler.start()
    job = Job()
    while True:
        job.tcp_detecting()
        time.sleep(SCHEDULER_INTERVAL)
