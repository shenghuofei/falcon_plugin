#!/bin/python
import urllib
import urllib2
import subprocess
import re
import time
import requests
import json

#must run src host,not in container


def mem_rate(containers):
    dirname='/sys/fs/cgroup/memory/system.slice/'
    message=[]
    timestamp=int(time.time())

    for k,v in containers.items():
        result=subprocess.check_output("systemctl --full | grep docker-"+k+"",shell=True).lstrip().split(' ')[0]
        filepath=dirname+"/"+result+"/memory.stat"
        #print filepath
        with open(filepath) as p:
           list = p.readlines()
           #print list
           for l in list:
               m=re.search(r'hierarchical_memory_limit ',l)
               n=re.search(r'total_rss ',l)
               if m:
                   limit=int(l.split(' ')[1])
               if n:
                   rss=int(l.split(' ')[1])
        rate=rss*100/limit
        free=limit-rss
        container_name=v
        #print str(rate)+'....'+container_name
        mes1={"metric":"container_memused_percent","endpoint":container_name,"timestamp":timestamp,"step":60,"value":rate,"counterType":"GAUGE","tags":""}
        message.append(mes1)
        mes2={"metric":"container_mem_free","endpoint":container_name,"timestamp":timestamp,"step":60,"value":free,"counterType":"GAUGE","tags":""}
        message.append(mes2)
    r = requests.post("http://127.0.0.1:1988/v1/push", data=json.dumps(message))
    #return message
    #print message

def cpu_rate(containers):
    dirname='/sys/fs/cgroup/cpuacct/system.slice/'
    message=[]
    timestamp=int(time.time())
    cpu_num=int(subprocess.check_output("grep -c processor /proc/cpuinfo",shell=True))
    for k,v in containers.items():
        result=subprocess.check_output("systemctl --full | grep docker-"+k+"",shell=True).lstrip().split(' ')[0]
        filepath=dirname+"/"+result+"/cpuacct.usage"
        total1=sum([int(r) for r in subprocess.check_output("grep 'cpu ' /proc/stat",shell=True).split(' ')[2:9]])
        cgroup_usage1=int(subprocess.check_output("cat %s" % filepath, shell=True))
        time.sleep(1)
        total2=sum([int(r) for r in subprocess.check_output("grep 'cpu ' /proc/stat",shell=True).split(' ')[2:9]])
        cgroup_usage2=int(subprocess.check_output("cat %s" % filepath, shell=True))
        cgroup_usage=float(cgroup_usage2-cgroup_usage1)
        total=float(total2-total1)
        cpu_rate=round(float(cgroup_usage*cpu_num/total/10000000*100),4)
        mes={"metric":"container_cpu_urate","endpoint":v,"timestamp":timestamp,"step":60,"value":cpu_rate,"counterType":"GAUGE","tags":""}
        message.append(mes)
    r = requests.post("http://127.0.0.1:1988/v1/push", data=json.dumps(message))
    #return message   
    #print message   
        
if __name__ == '__main__':
    ids=subprocess.check_output("docker ps|grep -v CONTAINER|awk '{print $1}'",shell=True).split('\n')[:-1]
    names=subprocess.check_output("docker ps|grep -v CONTAINER|awk '{print $NF}'",shell=True).split('\n')[:-1]
    containers=dict(zip(ids,names))
    #payload=[]
    #payload=mem_rate(containers)
    #print payload
    #data=json.dumps(payload)
    #r = requests.post("http://127.0.0.1:1988/v1/push", data=json.dumps(payload))
    #print r.text
    mem_rate(containers)
    cpu_rate(containers)
