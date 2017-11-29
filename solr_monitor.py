#!/usr/bin/python
import os, time

import subprocess
from subprocess import Popen, PIPE

from prometheus_client import start_http_server, Gauge

import platform
LOC_HOSTNAME = platform.node()

# --- Metrics:
num_of_hosts = Gauge('num_of_plugged_hosts', 'Number of plugged host.')

def get_metrics():
    command = 'h=`netstat -anp --tcp | grep -E ":8983.*" -o | grep -E "[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}" -o | sort`; num=`echo $h | wc -w` && num2=`echo $h | tr " " "\n" | uniq -c | sort -nr | wc -w`; echo $num2'
    netstat = subprocess.Popen( command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE )
    out = netstat.communicate()[0]
    num, b = out.split( "\n" )
    num = int(num)/2
    print("num %s" % num)
    num_of_hosts.set( num )

def main():
    start_http_server(8005)
    print("Running on 8005")
    while True:
        get_metrics()
        time.sleep(10)

if __name__ == '__main__':
    main()
