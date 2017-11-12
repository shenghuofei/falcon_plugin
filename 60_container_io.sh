#!/bin/bash

#must run in container

process=($(ls /proc | grep -P '\d+'))
read_total=0
write_total=0
endpoint=$(hostname)
for p in ${process[@]}
do
    read_bytes=$(grep '^read_bytes' /proc/${p}/io 2>/dev/null|awk '{print $2}')
    write_bytes=$(grep '^write_bytes' /proc/${p}/io 2>/dev/null|awk '{print $2}')
    if [ "x$read_bytes" == "x" ] ; then
        read_bytes=0
    fi
    if [ "x$write_bytes" == "x" ] ; then
        write_bytes=0
    fi
    read_total=$[read_total+read_bytes]
    write_total=$[write_total+write_bytes]
done
timestamp=$(date +%s)
echo "[{\"metric\": \"container_io_read\", \"value\": $read_total, \"endpoint\": \"$endpoint\", \"tags\": \"unit=bytes/s\", \"timestamp\": $timestamp, \"counterType\": \"COUNTER\", \"step\": 60},{\"metric\": \"container_io_write\", \"value\": $write_total, \"endpoint\": \"$endpoint\", \"tags\": \"unit=bytes/s\", \"timestamp\": $timestamp, \"counterType\": \"COUNTER\", \"step\": 60}]"
