#!/bin/bash

MAX_CPU_USAGE=30 #for limiting processes matching the query
MAX_CPU_USAGE2=60 #for reporting (and optionally limiting) any other process

# Specify the log file location
LOG_FILE="/var/log/cpulimit.log"

query='[v]scode-server'
if [[ $1 ]]; then
    query=${1}
fi

while true; do
    #get the processes of interest and see if they are using too much cpu
    PIDS=$(ps aux | grep ${query} | awk '{print $2}')
    if [ -z "$PIDS" ]; then
        echo "[$(date)] No ${query} processes found." | tee -a $LOG_FILE
    else
        # Apply the CPU limit to each offending process
        for PID in $PIDS
        do
            cpulimit -p $PID -l $MAX_CPU_USAGE &
            echo "[$(date)] CPU limit of $MAX_CPU_USAGE% applied to process with PID: $PID" | tee -a $LOG_FILE
        done
    fi

    #see if there are any other processes using too much cpu
    #procs=$(ps ax -o pid,%cpu,%mem,args)
    PIDS=$(ps aux | grep -v PID | awk '{print $2}')
    for pid in ${PIDS}; do
        res=$(ps -p $pid -o %cpu,args | grep -v %CPU)
        cpuu=$(echo ${res} | awk '{print $1}')
        args=$(echo ${res} | awk '{print $2}')
        if [[ -z ${cpuu} ]]; then continue; fi
        if (( $(echo "${cpuu} > ${MAX_CPU_USAGE2}" | bc -l) )); then
            echo "cpuu of ${pid} is ${cpuu}"
        fi
    done
    # Sleep for a specified amount of time before checking again
    sleep 5
done