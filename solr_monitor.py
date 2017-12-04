#!/usr/bin/python
# gDiff = Gauge( 'diffsk4_seconds', 'Difference between posted_at and real_posted_at [from ' + str( solr_dns ) + ']', [ 'channel', 'source', 'solrdtsrc', 'username' ] )
# gDiff.labels( channel=doc[ 'channel' ], source=doc[ 'source' ], solrdtsrc=str( solr ), username=str( usrnm ) ).set( it_posted_at - it_real_posted_at )
import os, time

import subprocess
from subprocess import Popen, PIPE

from prometheus_client import start_http_server, Gauge

import platform
LOC_HOSTNAME = platform.node()

# --- Metrics:
num_of_hosts = Gauge('num_of_plugged_hosts', 'Number of plugged host.')
host = Gauge('host', 'Plugged host.', ['ip'])
#status_traceroute = Gauge('status_traceroute', 'Status host (by traceroute)!);

def get_metrics():
#    command = 'ping -c 2 %s | tail -n 2 | grep "0 received"' % machine
#    command = 'h=`netstat -anp --tcp | grep -E ":8983.*" -o | grep -E "[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}" -o | sort`; num=`echo $h | wc -w`; echo $num'
#    command = 'h=`netstat -anp --tcp | grep -E ":8983.*" -o | grep -E "[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}" -o | sort`; num=`echo $h | wc -w` && num2=`echo $h | tr " " "\n" | uniq -c | sort -nr | wc -w`; echo $num2'

    command = 'h=`netstat -anp --tcp | grep -E ":8983.*" -o | grep -E "[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}" -o | sort`; echo $h | tr " " "\n" | uniq -c | sort -nr | grep -E "[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}" -o;'
    netstat = subprocess.Popen( command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE )
    out = netstat.communicate()[0]
    #print netstat
    #print out
    hosts = out.split("\n")
    num_hosts = 0
    for h in hosts:
        if h != '':
            host.labels( ip=str(h) ).set( 1 )
            #print("host_ip = %s" %h)
            num_hosts = num_hosts + 1
    #num, b = out.split( "\n" )
    #num = subprocess.call(command, shell=True)
    #num = int(num)/2
    #print("num %s" % num_hosts)
    num_of_hosts.set( num_hosts )

def main():
    start_http_server(8005)
    print("Running on 8005")
    while True:
        get_metrics()
        time.sleep(10)

if __name__ == '__main__':
    main()
