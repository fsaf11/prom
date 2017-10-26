import os
from os import path

import subprocess
from subprocess import Popen, PIPE

import time

from prometheus_client import start_http_server, Gauge

import platform
LOC_HOSTNAME = platform.node()

# --- Metrics:
statusPingTo = Gauge('ibm_status_ping', 'Status host (by ping)!', [ 'ip', 'orig_hostname', 'dest_hostname' ])
statusTracerouteTo = Gauge( 'ibm_status_traceroute', 'Status host (by traceroute)!', [ 'ip', 'orig_hostname', 'dest_hostname' ]) ;

PATH='./machines.txt'

def get_metrics():
    machines = open(PATH, 'r')

    for line in machines:
        MACHINE = line.replace("\n", "")
        IP, HOSTNAME = MACHINE.split(" ")
        
        # Setting ping metric:
        command = 'ping -c 5 %s | tail -n 2 | grep "0 received"' % IP
        ping = subprocess.call(command, shell=True)
        if ping == 1:
            statusPingTo.labels( ip=IP, orig_hostname=LOC_HOSTNAME, dest_hostname=HOSTNAME ).set( 1 )
        else:
            statusPingTo.labels( ip=IP, orig_hostname=LOC_HOSTNAME, dest_hostname=HOSTNAME ).set( 0 )
        
        # Setting traceroute metric:
        command = 'result=`traceroute -n %s | tail -n 1 | grep %s | cut -d " " -f4` && if [ "$result" = "%s" ] ; then echo $result; echo 1 ; else echo $result; echo -1; fi' % (IP,IP,IP)
        traceroute = subprocess.Popen( command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE )
        out = traceroute.communicate()[0]
        a, result, b = out.split( "\n" )
        if int( result ) == 1:
            statusTracerouteTo.labels( ip=IP, orig_hostname=LOC_HOSTNAME, dest_hostname=HOSTNAME ).set( 1 )
        else:
            statusTracerouteTo.labels( ip=IP, orig_hostname=LOC_HOSTNAME, dest_hostname=HOSTNAME ).set( 0 )   
        
def main():
    start_http_server(8001)
    print("Running on 8001")
    while True:
        if os.path.isfile(PATH) and os.access(PATH, os.R_OK):
            get_metrics()
        else:
            print('Either file <machines.txt> is missing or is not readable!')
        time.sleep(1)

if __name__ == '__main__':
    main()
