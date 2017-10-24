sudo su && cd /usr/local && sudo mkdir prometheus_components && cd /usr/local/prometheus_components && sudo mkdir python_scripts && cd /usr/local/prometheus_components/python_scripts && yum -y install python-pip && pip install --upgrade pip && pip2 install prometheus-client
wget https://github.com/fsaf11/prom/blob/master/ibm_machine_monitor.py &
#create machines.txt
python2 ibm_machine_monitor.py &
