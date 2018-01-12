#!/usr/bin/python
import os
from os import path

import subprocess
from subprocess import Popen, PIPE

import time

from prometheus_client import start_http_server, Gauge

import platform
LOC_HOSTNAME = platform.node()

global PRIVATE_IP
PRIVATE_IP = ''

# --- Metrics
# Eliminado o label 'orig_hostname'! Ja existe a 'instance'
# Eliminados os labels 'pckt_loss_percent', 'time_ms' da metrica 'statusPingTo'! Agora tem suas proprias metricas.
#statusPingTo = Gauge('ibm_status_ping', 'Status host (by ping)!', [ 'ip', 'orig_hostname', 'pckt_loss_percent', 'time_ms' ])
statusPingTo = Gauge('ibm_status_ping', 'Status host (by ping)!', [ 'pv_ip', 'ip', 'dest_hostname'])
pingPcktLossPercent = Gauge('ibm_ping_pckt_loss_percent', 'Percent of packet loss (by ping)!', [ 'pv_ip', 'ip', 'dest_hostname'])
pingTimeMs = Gauge('ibm_ping_time_ms', 'Response time [ms] (by ping).', [ 'pv_ip', 'ip', 'dest_hostname'])
statusTracerouteTo = Gauge( 'ibm_status_traceroute', 'Status host (by traceroute)!', [ 'pv_ip', 'ip', 'dest_hostname' ]) ;
# --- Metrics

PATH='./machines.txt'

def get_metrics():
    machines = open(PATH, 'r')

    for line in machines:
        MACHINE = line.replace("\n", "")
        IP, HOSTNAME = MACHINE.split(" ")
        
        """ Setting ping metric """
        #command = 'ping -c 5 %s | tail -n 2 | grep "0 received"' % IP
        #ping = subprocess.call(command, shell=True)
        #if ping == 1:
        #    statusPingTo.labels( ip=IP, orig_hostname=LOC_HOSTNAME, dest_hostname=HOSTNAME ).set( 1 )
        #else:
        #    statusPingTo.labels( ip=IP, orig_hostname=LOC_HOSTNAME, dest_hostname=HOSTNAME ).set( 0 )
        command = 'PING_OUTPUT=`ping -c 5 %s | tail -n 2 | head -n 1 | sed s/", "/";"/g | sed s/" packet loss;time "/""/g | sed s/"ms"/";"/g | cut -d ";" -f3-5` && echo $PING_OUTPUT' % IP
        ping = subprocess.Popen( command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE )
        out, err = ping.communicate()
        out = out.replace("\n", "")
        out = out.replace("%", ";")
        PERC = "0"
        MS = "0"
        if "errors" in out:
            NUMERRORS, PERC, MS, DISCARD = out.split(";")
            PERC = int(PERC)           
            if PERC == 100:
                #statusPingTo.labels( ip=IP, dest_hostname=HOSTNAME, pckt_loss_percent=PERC, time_ms=MS ).set( 0 )
                statusPingTo.labels( pv_ip=PRIVATE_IP, ip=IP, dest_hostname=HOSTNAME ).set( 0 )
                #print "Unreachable! [%s percents packet loss, time = %sms]" % (perc, ms)
            else:
                #statusPingTo.labels( pv_ip=PRIVATE_IP, ip=IP dest_hostname=HOSTNAME, pckt_loss_percent=PERC, time_ms=MS ).set( 1 )
                statusPingTo.labels( pv_ip=PRIVATE_IP, ip=IP, dest_hostname=HOSTNAME ).set( 1 )
                #print "OK! %s percents packet loss, time = %sms" % (perc, ms)
        else:
            PERC, MS, DISCARD = out.split(";")
            PERC = int(PERC)
            if PERC == 100:
                #statusPingTo.labels( ip=IP, dest_hostname=HOSTNAME, pckt_loss_percent=PERC, time_ms=MS ).set( 0 )
                statusPingTo.labels( pv_ip=PRIVATE_IP, ip=IP, dest_hostname=HOSTNAME ).set( 0 )
                #print "Unreachable! [%s percents packet loss, time = %sms]" % (perc, ms)
            else:
                #statusPingTo.labels( ip=IP, dest_hostname=HOSTNAME, pckt_loss_percent=PERC, time_ms=MS ).set( 1 )
                statusPingTo.labels( pv_ip=PRIVATE_IP, ip=IP, dest_hostname=HOSTNAME ).set( 1 )
                #print "OK! %s percents packet loss, time = %sms" % (perc, ms)
                
        # Setting traceroute metric:
        command = 'result=`traceroute -n %s | tail -n 1 | grep %s | cut -d " " -f4` && if [ "$result" = "%s" ] ; then echo $result; echo 1 ; else echo $result; echo -1; fi' % (IP,IP,IP)
        traceroute = subprocess.Popen( command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE )
        out = traceroute.communicate()[0]
        a, result, b = out.split( "\n" )
        if int( result ) == 1:
            statusTracerouteTo.labels( pv_ip=PRIVATE_IP, ip=IP, dest_hostname=HOSTNAME ).set( 1 )
        else:
            statusTracerouteTo.labels( pv_ip=PRIVATE_IP, ip=IP, dest_hostname=HOSTNAME ).set( 0 )   
            
        pingPcktLossPercent.labels( pv_ip=PRIVATE_IP, ip=IP, dest_hostname=HOSTNAME ).set( int(PERC) )
        pingTimeMs.labels( pv_ip=PRIVATE_IP, ip=IP, dest_hostname=HOSTNAME ).set( int(MS) )        
        
def main():
    command = 'pv=`ip a | grep -E "inet 10.*/" | sed -r "s/(inet |\/)/;/g" | cut -d ";" -f2` ; echo $pv'
    result_cmd = subprocess.Popen( command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE )
    out = result_cmd.communicate()[0]
    global PRIVATE_IP
    PRIVATE_IP, lixo = out.split( "\n" )
    #print private_ip
    start_http_server(8001)
    print("Running on 8001")
    while True:
        if os.path.isfile(PATH) and os.access(PATH, os.R_OK):
            get_metrics()
        else:
            print('Either file <machines.txt> is missing or is not readable!')
        time.sleep(3)

if __name__ == '__main__':
    main()
